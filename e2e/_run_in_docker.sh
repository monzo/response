#!/bin/bash

set -euo pipefail

pip install -r requirements.txt
pytest -v
