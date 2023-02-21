set -e

flask init-db
flask --debug run --host=0.0.0.0
