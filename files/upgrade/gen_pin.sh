#! /usr/bin/env bash
if [ $# -eq 0 ]; then
  echo "[usage]: $0 version"
  exit 1
fi
python3 _gen_pin.py "$1" | tee pin.txt.rc
