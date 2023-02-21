from dotenv import load_dotenv
import os


load_dotenv()


SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASE = {
    "database": os.environ.get("POSTGRES_DB"),
    "port": os.environ.get("POSTGRES_PORT"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
}

