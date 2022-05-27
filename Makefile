CWD=$(shell pwd)

.PHONY: test

test:
	python tests/test_query.py
