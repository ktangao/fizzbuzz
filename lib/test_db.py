#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from db import RequestsDB

class TestRequestsDB(unittest.TestCase):
    def setUp(self):
        self.db = RequestsDB(database=".test_add")

    def tearDown(self):
        self.db.clear()

    def test_add_requests(self):
        db = self.db
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

    def test_get_req(self):
        db = self.db
        db.add("3_5_20_fizz_buzz", "toto")

        rec = db.get("3_5_20_fizz_buzz")
        self.assertEqual(rec, ("toto",))

        rec = db.get("toto")
        self.assertEqual(rec, None)

    def test_most_hit(self):
        db = self.db
        db.add("3_5_20_fizz_buzz", "toto")
        db.add("test", "titi")
        db.add("3_5_20_fizz_buzz", "toto")
        db.add("3_5_20_fizz_buzz", "toto")

        res = db.get_most_hit(max_rows=1)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], ("3_5_20_fizz_buzz", "toto", 3))

        res = db.get_most_hit(max_rows=2)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0], ("3_5_20_fizz_buzz", "toto", 3))
        self.assertEqual(res[1], ("test", "titi", 1))

        # we dont have more than 2 rows in the db
        res = db.get_most_hit(max_rows=3)
        self.assertEqual(len(res), 2)

if __name__ == "__main__":
    unittest.main()
