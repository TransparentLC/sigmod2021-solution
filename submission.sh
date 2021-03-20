#!/usr/bin/env bash

if [ -d .reprozip-trace ]; then
  rm -rf .reprozip-trace
fi
if [ -f submission.rpz ]; then
  rm submission.rpz
fi
if [ -f extract-test.csv ]; then
  rm extract-test.csv
fi
if [ -f output.csv ]; then
  rm output.csv
fi
reprozip trace python3 main.py
reprozip pack submission.rpz