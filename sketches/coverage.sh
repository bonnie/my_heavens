#!/bin/zsh

coverage run --source=. --omit="./env/*","./sidereal/*","./run_tests.py","./tests/*" run_tests.py
coverage report -m
