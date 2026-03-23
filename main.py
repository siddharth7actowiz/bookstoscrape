from config import *
from utils import *
from parser import parser, get_products_data, cretae_pages_urls_
from db import *
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def main():
    st = time.time()

    con = make_connection()
    cursor = con.cursor()

    create_table(cursor)

    # create and insert page URLs
    urls_data = cretae_pages_urls_(url)
    insert_into_db(cursor, con, urls_data, urls_tab)  
    con.commit()                                      

   
   # fectrating data from req with multithreading
    with ThreadPoolExecutor(max_workers=8) as tpe:
        future = tpe.submit(parser)
        parsed_data = future.result() 
  
    #inserts data table
    insert_into_db(cursor, con, parsed_data,data_tab)               

    # fetch product entries and scrape in parallel
    product_entries = list(fetch_urls(               
        "books_to_scrape",
        "book_name",
        "product_url",
        "image_url",
        "price",
        "availability"
    ))
    print(f"Products to scrape: {len(product_entries)}")  # sanity check

    all_products = []
    with ThreadPoolExecutor(max_workers=10) as tpe:
        futures = {tpe.submit(get_products_data, entry): entry
                   for entry in product_entries}
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    all_products.append(result)
            except Exception as e:
                print(f"Error processing product: {e}")

    print(f"Products detailed: {len(all_products)}")  

    insert_into_db(cursor, con, all_products, prods)
    con.commit()

    cursor.close()
    con.close()
    print(f"Total time: {time.time() - st:.2f}s")


if __name__ == "__main__":
    main()
