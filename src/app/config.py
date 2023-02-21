from dotenv import load_dotenv
import os
from dotenv import load_dotenv


load_dotenv()


SECRET_KEY = os.environ.get("SECRET_KEY")

DATABASE = {
    'host': os.environ.get("POSTGRES_HOST"),
    'port': os.environ.get("POSTGRES_PORT"),
    'database': os.environ.get("POSTGRES_DB"),
    'user': os.environ.get("POSTGRES_USER"),
    'password': os.environ.get("POSTGRES_PASSWORD")
}
