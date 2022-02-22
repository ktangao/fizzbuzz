#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tornado import testing, gen
from tornado.escape import json_encode

from lib.db import RequestsDB
from server import getApp

class TestLoadFizzBuzzServer(testing.AsyncHTTPTestCase):
	HTTP_STATUS_OK = 200

	def get_app(self):
		self.db = RequestsDB(database=".testload.db")
		return getApp(self.db)

	@testing.gen_test
	async def test_500_parallel_req(self):
		self.db.clear()
		load = 500
		results = await gen.multi([
			self.http_client.fetch(
				self.get_url('/fizzbuzz/sequence'),
				method="POST",
				headers={"Content-Type": "application/json"},
				body=json_encode({"int1": 3, "int2": 5, "limit": 100, "str1": "fizz", "str2": "buzz"}),
				connect_timeout=10,
				request_timeout=10,
			) for _ in range(load)
		])
		for res in results:
			self.assertEqual(res.code, self.HTTP_STATUS_OK)

		res = self.db.get_most_hit()
		for rec in res:
			print("id: %s, occ: %s", rec[0], rec[2])
		self.assertEqual(len(res), 1)
		# check that the number of occurences is equals to the load
		self.assertEqual(res[0][2], load)
		self.db.clear()

if __name__ == "__main__":
	testing.main()
