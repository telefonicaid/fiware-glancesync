#!/bin/bash

cd $(dirname $0)/../tests
export PYTHONPATH=..
python -m unittest discover
