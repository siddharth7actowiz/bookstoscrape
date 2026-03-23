import mysql.connector
from mysql.connector import pooling
from config import *

# Create a global connection pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,  # adjust based on your workload
    **DB_CONFIG
)

def make_connection():
    return connection_pool.get_connection()

def create_table(cursor):
    ddl1=f""" CREATE TABLE IF NOT EXISTS books_url(
        id INT AUTO_INCREMENT PRIMARY KEY,
        page_no int,
        page_url text,
        status varchar(200)
    )"""
    
    cursor.execute(ddl1)
    ddl2=f"""
    CREATE TABLE IF NOT EXISTS books_to_scrape(
        id INT AUTO_INCREMENT PRIMARY KEY,
        book_name VARCHAR(255),
        price VARCHAR(20),
        image_url TEXT,
        product_url TEXT,
        availability VARCHAR(50)
    
    );
    """
    cursor.execute(ddl2)

def insert_into_db(cursor, con, data,tab):

    if not data:
        print("No data to insert")
        return

    cols = list(data[0].keys())
    col_str = ", ".join(cols)
    placeholders = ", ".join(["%s"] * len(cols))

    query = f"""
    INSERT INTO {tab} ({col_str}) 
    VALUES ({placeholders})
    """

    values = [tuple(row.get(col) for col in cols) for row in data]

    try:
        cursor.executemany(query, values)
        con.commit()
        print(f"{cursor.rowcount} rows inserted")

    except Exception as e:
        con.rollback()
        print("Insert error:", e)