#!/bin/bash

# Launch five instances of workers
start python worker/worker.py 'localhost' 9090 &
start python worker/worker.py 'localhost' 9090 &
start python worker/worker.py 'localhost' 9090 &
start python worker/worker.py 'localhost' 9090 &
start python worker/worker.py 'localhost' 9090
