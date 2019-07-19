#!/bin/bash

set -euo pipefail

pip install -r requirements-dev.txt
pytest
