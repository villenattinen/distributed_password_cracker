#!/bin/bash

# Launch the server
python server/server.py &

# Launch five instances of the worker
python worker/worker.py 'localhost' 9090 &
python worker/worker.py 'localhost' 9090 &
python worker/worker.py 'localhost' 9090 &
python worker/worker.py 'localhost' 9090 &
python worker/worker.py 'localhost' 9090
