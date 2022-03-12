# fizzbuzz rest server

This is an implementation of a fizzbuzz REST server. The original fizz-buzz consists in writing all numbers from 1 to 100, and just replacing all multiples of 3 by "fizz", all multiples of 5 by "buzz", and all multiples of 15 by "fizzbuzz". The output would look like this: "1,2,fizz,4,buzz,fizz,7,8,fizz,buzz,11,fizz,13,14,fizzbuzz,16,...".

In this adapted version of the original fizzbuzz problem, a first endpoint is exposed allowing the user to provide the following parameters:
* int1
* int2
* limit
* str1
* str2

The exposed API returns a list of strings with numbers from 1 to limit, where: all multiples of int1 are replaced by str1, all multiples of int2 are replaced by str2, all multiples of int1 and int2 are replaced by str1str2.

A second endpoint, "statistics" is also esposed to allow any user to retrieve the 10 most queried fizzbuzz sequences.

## Tests

In addition to the available unit tests, a load test is available in file *test_load_server.py* to ensure the service can handle several requests at the same time 
All the tests can be executed with the command `sh run_tests.sh`.

## Dependencies

* python3.6 or higher.
* poetry is used as python package manager.
* tornado library is used to implement the REST server.

## Start the server

Make sure you have docker-compose installed and then run

  `docker-compose up`

## Examples

  $ `curl -X POST 0.0.0.0:8888/fizzbuzz/sequence --header "Content-Type:application/json" --data @data.json`
  > `{"sequence": "1,2,fizz,4,buzz,fizz,7,8,fizz,buzz,11,fizz,13,14,fizzbuzz,16,17,fizz,19,buzz"}`

  $ `curl -X GET 0.0.0.0:8888/fizzbuzz/statistics`
  > `{"stats": [{"int1": "3", "int2": "5", "limit": "20", "str1": "fizz", "str2": "bizz", "sequence": "1,2,fizz,4,bizz,fizz,7,8,fizz,bizz,11,fizz,13,14,fizzbizz,16,17,fizz,19,bizz", "nb_occurences": 602}]}`

  Note that the stats are refreshed once each 24 hours by default. So to view new values, restart the server.

## TODO

* support HTTPS connection
* implement a access control layer
* backup procedure for the db
* redirect logs to file on disk with file rotation
