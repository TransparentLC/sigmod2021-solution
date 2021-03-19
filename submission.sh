#!/usr/bin/env bash

if [ -d .reprozip-trace ]; then
  rm -rf .reprozip-trace
fi
if [ -f submission.rpz ]; then
  rm submission.rpz
fi
reprozip trace python3 main.py
reprozip pack submission.rpz