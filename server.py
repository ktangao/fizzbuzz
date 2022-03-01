#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import partial
import logging
import os
import signal
import sys
import time

from tornado.escape import (json_decode, json_encode)
from tornado.ioloop import IOLoop
from tornado.web import (RequestHandler, Application)

from lib.db import RequestsDB
from lib.fizzbuzz import FizzBuzzSeqGenerator

logging.basicConfig(format="%(name)s: %(asctime)s: %(levelname)s: %(message)s")
LOGGER = logging.getLogger("fizzbuzz")
LOGGER.setLevel(logging.INFO)
IS_SERVER_STARTED = False
REQUESTS_QUEUE = []
MOST_QUERIED = {}
STATS_CACHE = None

__all__ = (
    "getApp",
)

# {{{ Helpers

def flush_queue(db):
    global REQUESTS_QUEUE
    db.add_batch(REQUESTS_QUEUE)
    REQUESTS_QUEUE = []

# }}}
# {{{ FizzBuzz Handler

class FizzBuzzHandler(RequestHandler):
    CONTENT_TYPES = ["application/json", "application/x-json"]
    REPLY_CONTENT_TYPE = "application/json; charset=UTF-8"
    HTTP_BAD_REQ_CODE = 400
    HTTP_STATUS_OK = 200
    HTTP_STATUS_NO_CONTENT = 204

    def _check_content_type(self):
        content_type = self.request.headers.get("Content-Type")
        if content_type is None:
            self.error = {
                "code": self.HTTP_BAD_REQ_CODE,
                "msg": "invalid Content-Type",
            }
            return False
        content_type = content_type.lstrip()
        for expected_ctype in self.CONTENT_TYPES:
            if content_type.startswith(expected_ctype):
                return True
        self.error = {
            "code": self.HTTP_BAD_REQ_CODE,
            "msg": (f"accepted content types are: {self.CONTENT_TYPES}, "
                    f" got {content_type}"),
        }
        return False

    def _set_reply_content_type(self):
        self.set_header("Content-Type", self.REPLY_CONTENT_TYPE)

    def _reply_error_and_finish(self):
        assert (self.error)
        self._set_reply_content_type()
        self.set_status(self.error.get("code"))
        self.finish(json_encode({"error": self.error.get("msg")}))
        LOGGER.info("error on request: %s", self.error)

    def _reply_success(self, key, val):
        self._set_reply_content_type()
        self.set_status(self.HTTP_STATUS_OK)
        self.finish(json_encode({key: val}))

# }}}
# {{{ FizzBuzz Sequence handler

class FizzBuzzSequenceHandler(FizzBuzzHandler):
    def initialize(self, db=None, queue_max_size=100, **kwargs):
        self.db = db
        self.queue_max_size = queue_max_size
        self.error = None

    def prepare(self):
        if not self._check_content_type():
            return
        self.retrievedArgs = {}
        for key in ["int1", "int2", "limit", "str1", "str2"]:
            body = json_decode(self.request.body)
            val = body.get(key)
            if val is None:
                self.error = {
                    "code": self.HTTP_BAD_REQ_CODE,
                    "msg": f"{key} is missing in the request body"
                }
                return
            self.retrievedArgs[key] = str(val).strip()

    async def post(self):
        if self.error is not None:
            self._reply_error_and_finish()
            return

        try:
            seqGenerator = FizzBuzzSeqGenerator(**self.retrievedArgs)
        except ValueError as err:
            self.error = {
                "code": self.HTTP_BAD_REQ_CODE,
                "msg": str(err),
            }
            self._reply_error_and_finish()
            return

        self.req_id = self._get_req_id()

        # check in the most queried cache first
        global MOST_QUERIED
        self.sequence = MOST_QUERIED.get(self.req_id)
        if self.sequence:
            self._reply_success("sequence", self.sequence)
            return

        # check if request is on the db just return the retrieved value.
        # make the db interaction asynchroneous.
        if self.db:
            self.sequence = await IOLoop.current().run_in_executor(
                None, partial(self.db.get, self.req_id))
            self.sequence = self.sequence[0] if self.sequence is not None else None
            if self.sequence:
                self._reply_success("sequence", self.sequence)
                return

        # Retrieving the sequence may take some time depending on the user
        # provided to the limit. So run this blocking part asynchronously
        # for a better handling of simultaneous requests.
        self.sequence = await IOLoop.current().run_in_executor(None, seqGenerator.sequence)
        self._reply_success("sequence", self.sequence)

    def on_finish(self):
        if self.error is not None:
            return

        global REQUESTS_QUEUE
        REQUESTS_QUEUE.append((self.req_id, self.sequence))
        if self.db and len(REQUESTS_QUEUE) >= self.queue_max_size:
            flush_queue(self.db)

    def _reply_success(self, key, val):
        super()._reply_success(key, val)
        LOGGER.info(f"successfull sequence generated for: %s", self.retrievedArgs)

    def _get_req_id(self):
        return (f"{self.retrievedArgs['int1']}_{self.retrievedArgs['int2']}_"
                f"{self.retrievedArgs['limit']}_{self.retrievedArgs['str1']}_"
                f"{self.retrievedArgs['str2']}")

# }}}
# {{{ FizzBuzz Statistics handler

class FizzBuzzStatisticsHandler(FizzBuzzHandler):
    def initialize(self, db, stats_cache_life_time=3600*24, **kwargs):
        self.db = db
        self.cache_life_time = stats_cache_life_time

    async def get(self):
        now = int(time.time())
        global STATS_CACHE
        if STATS_CACHE is not None and STATS_CACHE[0] + self.cache_life_time > now:
            #cache is still valid just serve it
            self._reply_success(STATS_CACHE[1])
            return

        global REQUESTS_QUEUE
        if REQUESTS_QUEUE:
            flush_queue(self.db)

        res = await IOLoop.current().run_in_executor(
            None, self.db.get_most_hit
        )

        global MOST_QUERIED
        MOST_QUERIED.clear()
        recs = []
        if res is not None:
            for rec in res:
                (int1, int2, limit, str1, str2) = rec[0].split("_")
                recs.append({
                    "int1": int1,
                    "int2": int2,
                    "limit": limit,
                    "str1": str1,
                    "str2": str2,
                    "sequence": rec[1],
                    "nb_occurences": rec[2]
                })
                MOST_QUERIED[rec[0]] = rec[1]

        STATS_CACHE = (now, recs)
        self._reply_success(recs)

    def _reply_success(self, stats):
        self._set_reply_content_type()
        self.set_status(self.HTTP_STATUS_OK if stats else self.HTTP_STATUS_NO_CONTENT)
        body = json_encode({"stats": stats}) if stats else None
        self.finish(body)

# }}}

def getApp(db=None, queue_max_size=100, stats_cache_life_time=3600*24):
    args = {
        "db": db,
        "queue_max_size": int(queue_max_size),
        "stats_cache_life_time": int(stats_cache_life_time),
    }
    return Application([
        (r"/fizzbuzz/sequence", FizzBuzzSequenceHandler, args),
        (r"/fizzbuzz/statistics", FizzBuzzStatisticsHandler, args),
    ])

def startServer():
    global IS_SERVER_STARTED
    if IS_SERVER_STARTED:
        return

    database = os.getenv("FIZZBUZZ_SERVER_DB_NAME", ".fizzbuzz.db")
    req_db = RequestsDB(database)

    stats_cache_life_time = os.getenv("FIZZBUZZ_STATS_CACHE_LIFE_TIME", 3600*24)
    queue_max_size = os.getenv("FIZZBUZZ_QUEUE_MAX_SIZE", "100")
    port = os.getenv("FIZZBUZZ_SERVER_PORT", "8888")
    app = getApp(req_db, queue_max_size, stats_cache_life_time)
    app.listen(int(port))
    LOGGER.info("server started")

    def signal_handler(signum, frame=None):
        flush_queue(req_db)
        stopServer()
        sys.exit(0)

    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, signal_handler)
    IS_SERVER_STARTED = True
    IOLoop.current().start()

def stopServer():
    global IS_SERVER_STARTED
    IOLoop.current().stop()
    IS_SERVER_STARTED = False
    LOGGER.info("server stoped")

if __name__ == "__main__":
    startServer()
