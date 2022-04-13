#!/bin/bash
set -eEuo pipefail

poetry run nbqa isort .
poetry run nbqa black .
poetry run isort utils
poetry run black utils
