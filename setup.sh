#!/bin/bash

# Checking python version
if python3 --version 2>&1 | grep -q '^Python 3\.9\.'; then
    echo 'Correct python version'
else
    echo 'You must have python 3.9 installed.'
    exit
fi

# Setting up dependencies
echo 'creating a virtual environment...'
python3 -m venv .venv
source .venv/bin/activate

echo 'installing python dependencies in the environment...'
python3 -m pip install -r requirements.txt

echo 'Finished setting up'
echo 'Now you need to activate the virtual environment by:'
echo '      source .venv/bin/activate'
echo 'run the server file using: python3 server.py'
