#!/bin/bash

if [ $# -eq 0 ]; then
  flask --app src/app --debug run
else
  flask --app src/app --debug "$@"
fi
