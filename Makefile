CWD=$(shell pwd)

.PHONY: view_data

view_data:
	python -m http.server 8000 --bind 127.0.0.1

compile_data:
	source venv/bin/activate; python tests/validate.py

