# Makefile for common developer tasks

install:
	pip install -r requirements.txt

lint:
	flake8 modules/reflective_autonomy

test:
	pytest tests

run:
	python modules/reflective_autonomy/loom_restore_script.py
