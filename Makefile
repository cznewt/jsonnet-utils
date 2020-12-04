CWD=$(shell pwd)

.PHONY: view_data

view_data:
	python -m http.server 8000 --bind 127.0.0.1

test:
	source venv/bin/activate; python tests/test_query.py
