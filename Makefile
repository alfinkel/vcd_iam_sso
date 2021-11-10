# -*- mode:makefile; coding:utf-8 -*-

install:
	pip install -q --upgrade pip setuptools
	pip install -q . --upgrade --upgrade-strategy eager

develop:
	pip install -q -e . --upgrade --upgrade-strategy eager
