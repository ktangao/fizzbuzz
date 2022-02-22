#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tornado import testing, gen
from tornado.escape import json_encode, json_decode

from lib.db import RequestsDB
from server import getApp

class TestFizzBuzzServer(testing.AsyncHTTPTestCase):
	HTTP_STATUS_OK = 200
	HTTP_STATUS_BAD_REQUEST = 400
	HTTP_STATUS_METHOD_NO_ALLOWED = 405

	def get_app(self):
		self.db = RequestsDB(database=".test.db")
		return getApp(self.db)

	def test_succcessfull_req(self):
		resp = self.fetch(
			"/fizzbuzz/sequence",
			method="POST",
			headers={"Content-Type": "application/json"},
			body=json_encode({"int1": 3, "int2": 5, "limit": 20, "str1": "fizz", "str2": "buzz"}),
		)
		self.assertEqual(resp.code, self.HTTP_STATUS_OK)
		res = json_decode(resp.body).get("sequence")
		want = "1,2,fizz,4,buzz,fizz,7,8,fizz,buzz,11,fizz,13,14,fizzbuzz,16,17,fizz,19,buzz"
		self.assertEqual(res, want)
		self.db.clear()

	def test_huge_request(self):
		resp = self.fetch(
			"/fizzbuzz/sequence",
			method="POST",
			headers={"Content-Type": "application/json"},
			body=json_encode({"int1": 3, "int2": 5, "limit": 1000000, "str1": "fizz", "str2": "buzz"}),
		)
		self.assertEqual(resp.code, self.HTTP_STATUS_OK)
		self.db.clear()

	def test_too_big_limit_request(self):
		limit = 10000000
		resp = self.fetch(
			"/fizzbuzz/sequence",
			method="POST",
			headers={"Content-Type": "application/json"},
			body=json_encode({"int1": 3, "int2": 5, "limit": limit, "str1": "fizz", "str2": "buzz"}),
		)
		self.assertEqual(resp.code, self.HTTP_STATUS_BAD_REQUEST)
		res = json_decode(resp.body).get("error")
		want = f"limit {limit} cannot be bigger that 1000000"
		self.assertEqual(res, want)

	def test_too_big_str_request(self):
		resp = self.fetch(
			"/fizzbuzz/sequence",
			method="POST",
			headers={"Content-Type": "application/json"},
			body=json_encode({"int1": 3, "int2": 5, "limit": 20, "str1": "fizz" * 100, "str2": "buzz"}),
		)
		self.assertEqual(resp.code, self.HTTP_STATUS_BAD_REQUEST)
		res = json_decode(resp.body).get("error")
		want = "max len of str1 and str2 is 100"
		self.assertEqual(res, want)

	def test_missing_argument(self):
		resp = self.fetch(
			"/fizzbuzz/sequence",
			method="POST",
			headers={"Content-Type": "application/json"},
			body=json_encode({"int1": 3, "int2": 5, "limit": 20, "str1": "fizz"}),
		)
		self.assertEqual(resp.code, self.HTTP_STATUS_BAD_REQUEST)
		res = json_decode(resp.body).get("error")
		want = "str2 is missing in the request body"
		self.assertEqual(res, want)

	def test_invalid_content_type(self):
		resp = self.fetch(
			"/fizzbuzz/sequence",
			method="POST",
			headers={"Content-Type": "application/xml"},
			body=json_encode({"int1": 3, "int2": 5, "limit": 20, "str1": "fizz", "str2": "buzz"}),
		)
		self.assertEqual(resp.code, self.HTTP_STATUS_BAD_REQUEST)
		res = json_decode(resp.body).get("error")
		want = ("accepted content types are: ['application/json', 'application/x-json'],  "
                "got application/xml")
		self.assertEqual(res, want)

	def test_unsupported_method(self):
		resp = self.fetch(
			"/fizzbuzz/sequence",
			method="GET",
		)
		self.assertEqual(resp.code, self.HTTP_STATUS_METHOD_NO_ALLOWED)

class TestLoadFizzBuzzServer(testing.AsyncHTTPTestCase):
	HTTP_STATUS_OK = 200

	def get_app(self):
		self.db = RequestsDB(database=".test.db")
		return getApp(self.db)

	@testing.gen_test
	async def test_500_parallel_req(self):
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
		self.db.clear()

if __name__ == "__main__":
	testing.main()
