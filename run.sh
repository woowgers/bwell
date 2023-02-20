#!/bin/sh

APP_PATH="$(dirname $0)/src/app"

if [ $# -eq 0 ]; then
  flask --app "$APP_PATH" --debug run
else
  flask --app "$APP_PATH" --debug "$@"
fi
