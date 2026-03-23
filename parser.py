from validation import Store
import requests
from urllib.parse import urljoin
from lxml import html
from config import url
from db import make_connection
base_url=url
import gzip
import os

def cretae_pages_urls_(st_url):
   url=st_url
   url_pages=[]
   page_num=1
   while url:
       url_pages.append({
           "page_no":page_num,
            "page_url":url,
            "status":"pending"
       })
       res=requests.get(url)
       tree=html.fromstring(res.text)
       next_page = tree.xpath('string(//li[@class="next"]/a/@href)')


       

       if next_page:
            url = urljoin(url,next_page)
            page_num += 1
       else:
            break

   return url_pages
       
def fetch_urls():
    conn = make_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT page_no,page_url FROM books_url WHERE status='pending';")

    for row in cursor:
        yield row[0],row[1]   # one URL at a time

    cursor.close()
    conn.close()


def update_q(field):
      conn = make_connection()
      cursor = conn.cursor()

      cursor.execute(
        "UPDATE books_url SET status=%s WHERE page_no=%s",
        ("responded", field)   # ✅ EXACT match of 2 params
    )

      conn.commit()

      cursor.close()
      conn.close()    

def parser():
    
   books_data = []
   os.makedirs("pages", exist_ok=True)

   for page_no , page_url in fetch_urls():
      print(f"Processing Page {page_no}: {page_url}")
      try:
         res=requests.get(page_url)
         file_path = f"pages/page_{page_no}.html.gz"
         with gzip.open(file_path, "wt", encoding="utf-8") as f:
                f.write(res.text)
         tree=html.fromstring(res.text)

         books = tree.xpath('//ol[@class="row"]/li')

         for book in books:
            try:
                  data = {
                     "book_name": book.xpath('.//h3/a/@title')[0],

                     "price": book.xpath('.//p[@class="price_color"]/text()')[0].replace("Â", ""),

                     

                     "image_url": urljoin(base_url, book.xpath('.//img/@src')[0]),

                     "product_url": urljoin(base_url, book.xpath('.//h3/a/@href')[0]),

                     "availability": book.xpath('.//p[@class="instock availability"]/text()')[1].strip()
                  }

                  # Optional validation
                  obj = Store(**data)
                  books_data.append(obj.model_dump())
                  update_q(page_no)
            except Exception as e:
                     print("Parse error:", e)
        
         
      except Exception as e:
          print("Error",parser.__name__,e)
      
   return books_data


