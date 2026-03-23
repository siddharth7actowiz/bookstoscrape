from validation import Store
import requests
from urllib.parse import urljoin
from lxml import html
from config import url
from db import fetch_urls, update_q
from utils import read_json
from config import JSON_PATH_FILE, start_url
import gzip
import os
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

base_url = url
xpaths = read_json(JSON_PATH_FILE)
print(xpaths)


# creating urls for next pages
def cretae_pages_urls_(url):
    url_pages = []
    page_num = 1

    while url:
        url_pages.append({
            "page_no": page_num,
            "page_url": url,
            "status": "pending"
        })
        res = requests.get(url)
        tree = html.fromstring(res.text)
        next_page = tree.xpath(xpaths.get("next_page"))

        if next_page:
            url = urljoin(url, next_page[0])
            page_num += 1
        else:
            break

    return url_pages


def parser():
    
   books_data = []
   os.makedirs("pages", exist_ok=True)
   for page_no , page_url in fetch_urls("books_url","page_no" , "page_url"):
      print(f"Processing Page {page_no}: {page_url}")
      try:
         res=requests.get(page_url)
         file_path = f"pages/page_{page_no}.html.gz"
         with gzip.open(file_path, "wt", encoding="utf-8") as f:
                f.write(res.text)
        
         tree=html.fromstring(res.text)
         books = tree.xpath(xpaths.get("books"))
         for book in books:
            try:
                  # FIX 1: availability xpath returns a single string with string(),
                  # so use [0] not [1] — or strip directly
                  availability = book.xpath(xpaths.get("availability"))
                  data = {
                     "book_name": book.xpath(xpaths.get("book_name"))[0],
                     "price": book.xpath(xpaths.get("price"))[0].replace("Â", ""),
                     "image_url": urljoin(base_url, book.xpath(xpaths.get("image_url"))[0]),
                     "product_url": urljoin(start_url, book.xpath(xpaths.get("product_url"))[0]),
                       "availability": book.xpath(xpaths.get("availability"))[0].strip(),
                     "status":"pending"
                  }
                  obj = Store(**data)
                  books_data.append(obj.model_dump())
                  
            except Exception as e:
                     print("Parse error:", e)

         # FIX 2: was filtering by "status" column with an int — must filter by page_no
         update_q("books_url", "page_no", page_no)

      except Exception as e:
          print("Error",parser.__name__,e)
      
   return books_data

def make_safe_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.replace(" ", "_")
    return name[:100]


def get_products_data(entry):
    name, url, img, price, avl = entry
    products=[]
    os.makedirs("products", exist_ok=True)
    print(f"Processing Product: {url}")

    try:
        res = requests.get(url)

        tree = html.fromstring(res.text)

        title = tree.xpath('//div[@class="product_main"]/h1/text()')
        desc_list = tree.xpath('//*[@id="content_inner"]/article/p/text()')

        # availability
        availability_list = tree.xpath('//p[@class="instock availability"]/text()')
        availability = " ".join([i.strip() for i in availability_list if i.strip()])

        match = re.search(r'\d+', availability)
        qt = int(match.group()) if match else 0

        # helper to safely extract first xpath result as string
        def get_text(xpath):
            val = tree.xpath(xpath)
            return val[0].strip() if val else None

        product = {
            "Name": title[0].strip() if title else name,
            
            "Book_Id": tree.xpath('string(//th[text()="UPC"]/following-sibling::td/text())'),
            "Categoery": tree.xpath('string(//ul[@class="breadcrumb"]/li[3]/a/text())'),
            "Description": desc_list[0].strip() if desc_list else None,
            "Product_Url" :url,
            "Image_Url": img,
            "Price": price,
            "Price_Inc_Tax": tree.xpath('string(//th[contains(text(), "Price (incl. tax)")]/following-sibling::td/text())'),
            "Tax": tree.xpath('string(//th[contains(text(), "Tax")]/following-sibling::td/text())'),
            "Availability": availability,
            "Quantity": qt
        }
        products.append(product)
        update_q("books_to_scrape", "product_url", url)
       

    except Exception as e:
        print("Error in get_products_data:", e)
        return None

    return products    
