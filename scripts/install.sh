#!/bin/sh

python3 -m venv "$(dirname "$0")"/../venv
"$(dirname "$0")"/../venv/bin/pip install -r "$(dirname "$0")"/../requirements.txt
"$(dirname "$0")"/../venv/bin/pip install ipmininet --no-deps
