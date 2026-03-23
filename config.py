from dotenv import load_dotenv
import os

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR")
FILE_PATH=os.getenv("FILE_PATH")                             

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME")
}

data_tab = "books_to_scrape"
urls_tab="books_url"

url="https://books.toscrape.com/"
start_url="https://books.toscrape.com/catalogue/page-1.html"