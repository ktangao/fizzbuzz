#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tornado import testing
from tornado.escape import json_encode, json_decode

from server import getApp

class TestFizzBuzzServer(testing.AsyncHTTPTestCase):
	HTTP_STATUS_OK = 200
	HTTP_STATUS_BAD_REQUEST = 400
	HTTP_STATUS_METHOD_NO_ALLOWED = 405

	def get_app(self):
		return getApp()

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

	def test_huge_request(self):
		resp = self.fetch(
			"/fizzbuzz/sequence",
			method="POST",
			headers={"Content-Type": "application/json"},
			body=json_encode({"int1": 3, "int2": 5, "limit": 1000000, "str1": "fizz", "str2": "buzz"}),
		)
		self.assertEqual(resp.code, self.HTTP_STATUS_OK)

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
	

if __name__ == "__main__":
	testing.main()
