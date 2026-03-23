from dotenv import load_dotenv
import os

load_dotenv()

JSON_PATH_FILE=r"D://bookstoscrape1//paths.json"
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
prods="products"
url="https://books.toscrape.com/"
start_url="https://books.toscrape.com/catalogue/"