#!/usr/bin/env bash
set -e
for d in 0*/; do (cd "$d" && echo ">> $d" && python3 generate_data.py && python3 analysis.py >/dev/null); done
echo "All projects rebuilt."
