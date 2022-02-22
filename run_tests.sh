#!/usr/bin/env sh

poetry run python3 lib/test_fizzbuzz.py
poetry run python3 lib/test_db.py
poetry run python3 -m tornado.testing test_server.py
poetry run python3 -m tornado.testing test_load_server.py
