from validation import Store
import requests
from urllib.parse import urljoin
from lxml import html
from config import url
from db import fetch_urls,update_q
import gzip
import os


base_url=url
#creating urls for next pages
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
       

#parsing data from urls of pages
def parser():
    
   books_data = []
   os.makedirs("pages", exist_ok=True)

   for page_no , page_url in fetch_urls():
      print(f"Processing Page {page_no}: {page_url}")
      try:
         res=requests.get(page_url)
         #saving each response 
         file_path = f"pages/page_{page_no}.html.gz"
         with gzip.open(file_path, "wt", encoding="utf-8") as f:
                f.write(res.text)
        
         #parsing with lxml
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

                  # Data validation
                  obj = Store(**data)
                  books_data.append(obj.model_dump())
                  #Updating url tables status from pending to responded 
                  update_q(page_no)
            except Exception as e:
                     print("Parse error:", e)
        
         
      except Exception as e:
          print("Error",parser.__name__,e)
      
   return books_data


