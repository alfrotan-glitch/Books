#!/bin/bash
# two workers (odd / even pages) -> tools/data/pages
cd "$(dirname "$0")"
python3 stage1.py $(seq 1 2 179) > data/stage1_a.log 2>&1 &
python3 stage1.py $(seq 2 2 179) > data/stage1_b.log 2>&1 &
wait
echo done >> data/stage1_a.log
