#!/bin/bash

cd $(dirname $0)/../tests/unit
export PYTHONPATH=../..
python -m unittest discover
