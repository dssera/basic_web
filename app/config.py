import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"D:\web\companies-app\.env")

DATABASE_URL = os.environ.get("DATABASE_URL")
API_SECRET_KEY = os.environ.get("API_SECRET_KEY")
