from dotenv import load_dotenv
import os


load_dotenv()


SECRET_KEY = os.environ.get("BWELL_SECRET_KEY")
DATABASE = {
    "database": os.environ.get("BWELL_DB_SCHEMA"),
    "host": os.environ.get("BWELL_DB_HOST"),
    "port": os.environ.get("BWELL_DB_PORT"),
    "user": os.environ.get("BWELL_DB_USER"),
    "password": os.environ.get("BWELL_DB_PASSWORD"),
}
