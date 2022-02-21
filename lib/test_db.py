#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from db import RequestsDB

class TestRequestsDB(unittest.TestCase):
	def test_add_requests(self):
		db = RequestsDB(database=".test_add")
		db.add("3_5_20_fizz_buzz", "toto")
		db.add("test", "titi")
		db.add("3_5_20_fizz_buzz", "toto")
		db.add("tata", "titi")

		con = db.get_db_connection()
		sql = "select * from requests"
		recs = con.cursor().execute(sql).fetchall()
		self.assertEqual(len(recs), 3)
		want = set([('3_5_20_fizz_buzz', 'toto', 2), ('test', 'titi', 1), ('tata', 'titi', 1)])
		self.assertEqual(want, set(recs))

		db.clear()

	def test_get_req(self):
		db = RequestsDB(database=".test_add")
		db.add("3_5_20_fizz_buzz", "toto")

		rec = db.get("3_5_20_fizz_buzz")
		self.assertEqual(rec, ("toto",))

		rec = db.get("toto")
		self.assertEqual(rec, None)

		db.clear()

if __name__ == "__main__":
	unittest.main()
