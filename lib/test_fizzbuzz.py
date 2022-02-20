#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from fizzbuzz import FizzBuzzSeqGenerator

class TestFizzBuzzSeqGenerator(unittest.TestCase):
	def test_int_as_invalid_str(self):
		want = "int1, int2 and limit must be integers"
		for (int1, int2, limit) in [("invalid", 5, 10),
								    (5, "invalid", 10),
                                    (3, 5, "invalid")]:
			with self.assertRaisesRegex(ValueError, want):
				FizzBuzzSeqGenerator(int1, int2, limit, "fizz", "buzz")

	def test_null_integer(self):
		want = "int1 and int2 cannot be null"
		for (int1, int2) in [(0, 3), (3, 0)]:
			with self.assertRaisesRegex(ValueError, want):
				FizzBuzzSeqGenerator(int1, int2, 10, "fizz", "buzz")

	def test_limit_lower_1(self):
		want = "the provided limit (.*) cannot be lower or equal to 1"
		for limit in [-1, 0, 1]:
			with self.assertRaisesRegex(ValueError, want):
				FizzBuzzSeqGenerator(3, 5, limit, "fizz", "buzz")

	def test_int1_bigger_than_limit(self):
		want = "int1 (.*) and int2 (.*) cannot be bigger than the limit (.*)"
		for (int1, int2) in [(3, 5), (5, 3)]:
			with self.assertRaisesRegex(ValueError, want):
				FizzBuzzSeqGenerator(int1, int2, 4, "fizz", "buzz")

	def test_str1_str2_not_string(self):
		want = "str1 and str2 must be of type string"
		for (str1, str2) in [("fizz", 2), (2, "buzz")]:
			with self.assertRaisesRegex(ValueError, want):
				FizzBuzzSeqGenerator(3, 5, 100, str1, str2)

	def test_sequence(self):
		for (int1, int2, limit, str1, str2) in [
			("3", "5", "20", "fizz", "buzz"),
			(3, 5, 20, "fizz", "buzz"),
			("03", "05", "020", "fizz", "buzz")
		]:
			fizzbuzz = FizzBuzzSeqGenerator(int1, int2, limit, str1, str2)
			seq = fizzbuzz.sequence()
			want = "1,2,fizz,4,buzz,fizz,7,8,fizz,buzz,11,fizz,13,14,fizzbuzz,16,17,fizz,19,buzz"
			self.assertEqual(seq, want)


if __name__ == "__main__":
	unittest.main()
