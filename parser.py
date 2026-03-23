from validation import Store
import requests
from urllib.parse import urljoin
from lxml import html
from config import url
from db import fetch_urls,update_q
from utils import read_json
from config import JSON_PATH_FILE,start_url
import gzip
import os
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

base_url=url
xpaths=read_json(JSON_PATH_FILE)

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
       next_page = tree.xpath(xpaths.get("next_page"))


       

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

   for page_no , page_url in fetch_urls("books_url","page_no" , "page_url"):
      print(f"Processing Page {page_no}: {page_url}")
      try:
         res=requests.get(page_url)
         #saving each response 
         file_path = f"pages/page_{page_no}.html.gz"
         with gzip.open(file_path, "wt", encoding="utf-8") as f:
                f.write(res.text)
        
         #parsing with lxml
         tree=html.fromstring(res.text)

         books = tree.xpath(xpaths.get("books"))

         for book in books:
            try:
                  data = {
                     "book_name": book.xpath(xpaths.get("book_name"))[0],

                     "price": book.xpath(xpaths.get("price"))[0].replace("Â", ""),
                     
                     "image_url": urljoin(base_url, book.xpath(xpaths.get("image_url"))[0]),

                     "product_url": urljoin(start_url, book.xpath(xpaths.get("product_url"))[0]),

                     "availability": book.xpath(xpaths.get("availability"))[1].strip(),
                     "status":"pending"
                  }

                  # Data validation
                  obj = Store(**data)
                  books_data.append(obj.model_dump())
                  
                  
            except Exception as e:
                     print("Parse error:", e)
         #Updating url tables status from pending to responded 
         update_q("books_url","status" ,page_no)   
      except Exception as e:
          print("Error",parser.__name__,e)
      
   return books_data


def make_safe_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.replace(" ", "_")
    return name[:100]


def get_products_data():
    products = []
    os.makedirs("products", exist_ok=True)

    for name, url, img, price, avl in fetch_urls(
        "books_to_scrape",
        "book_name",
        "product_url",
        "image_url",
        "price",
        "availability"
    ):
        print(f"Processing Product: {url}")

        try:
            res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})

            
            safe_name = make_safe_filename(name)
            file_path = f"products/{safe_name}.html.gz"

            # with gzip.open(file_path, "wt", encoding="utf-8") as f:
            #     f.write(res.text)

            tree = html.fromstring(res.text)

            
            title = tree.xpath('//div[@class="product_main"]/h1/text()')
            desc = tree.xpath('//*[@id="content_inner"]/article/p/text()')

            # availability
            availability_list = tree.xpath('//p[@class="instock availability"]/text()')
            availability = " ".join([i.strip() for i in availability_list if i.strip()])

            match = re.search(r'\d+', availability)
            qt = int(match.group()) if match else 0   

            # table fields (convert list → string)
            def get_text(xpath):
                val = tree.xpath(xpath)
                return val[0].strip() if val else None

            temp = {
                "Name": title[0].strip() if title else name,
                "Book_Id": tree.xpath('//*[@id="content_inner"]/article/table/tbody/tr[1]/td/text()'),
                "Categoery":tree.xpath('(//ul[@class="breadcrumb"]/li/a/text())[3]'),
                "Description": desc,
                "Image_Url": img,
                "Price": price,
                "Price_Inc_Tax": tree.xpath('//*[@id="content_inner"]/article/table/tbody/tr[4]/td/text()'),
                "Tax": tree.xpath('//*[@id="content_inner"]/article/table/tbody/tr[5]/td/text()'),
                "Availability": availability,   #
                "Quantity": qt
            }

            products.append(temp)

         
            update_q("books_to_scrape", "product_url", url)

        except Exception as e:
            print("Error in get_products_data:", e)

    print(f"Total products scraped: {len(products)}")
    return products