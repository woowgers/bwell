#!/bin/bash
set -e

if [ $# -eq 0 ]; then
  flask --debug run --host=0.0.0.0
else
  flask "$@"
fi
