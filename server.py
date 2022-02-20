#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os 
import logging

from tornado.escape import (json_decode, json_encode)
from tornado.ioloop import IOLoop
from tornado.web import (RequestHandler, Application)

from lib.fizzbuzz import FizzBuzzSeqGenerator

logging.basicConfig(format="%(name)s: %(asctime)s: %(levelname)s: %(message)s")
LOGGER = logging.getLogger("fizzbuzz")
LOGGER.setLevel(logging.INFO)

# {{{ FizzBuzz Request handler

class FizzBuzzHandler(RequestHandler):
	CONTENT_TYPES = ["application/json", "application/x-json"]
	REPLY_CONTENT_TYPE = "application/json; charset=UTF-8"
	HTTP_BAD_REQ_CODE = 400
	HTTP_STATUS_OK = 200
	
	def initialize(self):
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
		# Retrieving the sequence may take some time depending on the user
		# provided to the limit. So run this blocking part asynchronously
		# for a better handling of simultaneous requests.
		seq = await IOLoop.current().run_in_executor(None, seqGenerator.sequence)
		self._reply_success(seq)

	# {{{ Private helpers

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

	def _reply_success(self, sequence):
		self._set_reply_content_type()
		self.set_status(self.HTTP_STATUS_OK)
		self.finish(json_encode({"sequence": sequence}))
		LOGGER.info(f"successfull sequence generated for: %s", self.retrievedArgs)
		
	# }}}
# }}}

def app():
	return Application([
        (r"/fizzbuzz/sequence", FizzBuzzHandler),
    ])
	
if __name__ == "__main__":
	port = os.getenv("FIZZBUZZ_SERVER_PORT", "8888")
	app().listen(int(port))
	LOGGER.info("server started")
	IOLoop.current().start()
