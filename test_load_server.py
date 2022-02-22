#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tornado import testing, gen
from tornado.escape import json_encode, json_decode

from lib.db import RequestsDB
from server import getApp

class TestLoadFizzBuzzServer(testing.AsyncHTTPTestCase):
	HTTP_STATUS_OK = 200

	def get_app(self):
		self.db = RequestsDB(database=".testload.db")
		return getApp(self.db)

	async def load_server(self, load, limit=100):
		results = await gen.multi([
			self.http_client.fetch(
				self.get_url('/fizzbuzz/sequence'),
				method="POST",
				headers={"Content-Type": "application/json"},
				body=json_encode({
					"int1": 3,
					"int2": 5,
					"limit": limit,
					"str1": "fizz",
					"str2": "buzz",
				}),
				connect_timeout=10,
				request_timeout=10,
			) for _ in range(load)
		])
		return results

	@testing.gen_test
	async def test_500_parallel_req(self):
		self.db.clear()
		load = 500
		results = await self.load_server(load)
		for res in results:
			self.assertEqual(res.code, self.HTTP_STATUS_OK)

		res = self.db.get_most_hit()
		self.assertEqual(len(res), 1)
		# check that the number of occurences is equals to the load
		self.assertEqual(res[0][2], load)

		# test stats
		for limit in range(6, 20):
			load = limit * 2
			_ = await self.load_server(load, limit)

		res = await self.http_client.fetch(
			self.get_url('/fizzbuzz/statistics'),
			method="GET",
		)
		self.assertEqual(res.code, self.HTTP_STATUS_OK)
		stats = json_decode(res.body).get("stats")
		occs = [500, 38, 36, 34, 32, 30, 28, 26, 24, 22]
		for idx, stat in enumerate(stats):
			self.assertEqual(stat.get("nb_occurences"), occs[idx])

if __name__ == "__main__":
	testing.main()
