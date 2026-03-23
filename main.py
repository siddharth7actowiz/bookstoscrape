from config import *
from utils import *
from parser import cretae_pages_urls_,parser ,get_products_data
from db import *
import time
from concurrent.futures import ThreadPoolExecutor

def main():
    st=time.time()
   
    #making db cnnetion
    con = make_connection()
    cursor = con.cursor()

    create_table(cursor)

    # #urls creatng function 
    # urls_data=cretae_pages_urls_(start_url)

    # #insterts urls tbale
    # insert_into_db(cursor, con, urls_data,urls_tab)
  
    # ectrating data from req with multithreading
    # with ThreadPoolExecutor(max_workers=8) as tpe:
    #     future = tpe.submit(parser)
    #     parsed_data = future.result() 
  
    # #inserts data table
    # insert_into_db(cursor, con, parsed_data,data_tab)
    
    with ThreadPoolExecutor(max_workers=10) as tpe:
        future = tpe.submit(get_products_data)
        parsed_data = future.result() 
    
    insert_into_db(cursor,con,parsed_data,prods)
    cursor.close()
    con.close()
    print(time.time()-st)


if __name__ == "__main__":
    main()
  
