set -e

python -m flask --app app init-db
python -m flask --app app --debug run
