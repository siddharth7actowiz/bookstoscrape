import mysql.connector
from mysql.connector import pooling
from config import *

# Create a global connection pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=15,  # adjust based on your workload
    **DB_CONFIG
)

# DB Connetion
def make_connection():
    return connection_pool.get_connection()
#table  creton query
def create_table(cursor):
    ddl1=f""" CREATE TABLE IF NOT EXISTS {urls_tab}(
        id INT AUTO_INCREMENT PRIMARY KEY,
        page_no int,
        page_url text,
        status varchar(200)
    )"""
    
    cursor.execute(ddl1)
    ddl2=f"""
    CREATE TABLE IF NOT EXISTS {data_tab}(
        id INT AUTO_INCREMENT PRIMARY KEY,
        book_name VARCHAR(255),
        price VARCHAR(20),
        image_url TEXT,
        product_url TEXT,
        availability VARCHAR(50),
        status VARCHAR(50)
    
    );
    """
    cursor.execute(ddl2)

    ddl3=f'''
        CREATE TABLE IF NOT EXISTS {prods}(
         id INT AUTO_INCREMENT PRIMARY KEY,
         Name TEXT,
         Book_Id VARCHAR(100) UNIQUE,
         Categoery VARCHAR(20),
         Description TEXT,
         Image_Url TEXT,
         Price VARCHAR(10),
         Price_Inc_Tax VARCHAR(10),
         Tax VARCHAR(10),
         Availability VARCHAR(100),
         Quantity int
        );
    '''
    cursor.execute(ddl3)
# insert query
def insert_into_db(cursor, con, data, table_name, batch_size=100):
    if not data:
        return

    cols = list(data[0].keys())
    col_string = ", ".join(cols)
    placeholders = ", ".join(["%s"] * len(cols))

    query = f"INSERT INTO {table_name} ({col_string}) VALUES ({placeholders})"

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]

        values = [tuple(item[col] for col in cols) for item in batch]

        cursor.executemany(query, values)
        con.commit()

        print(f"Inserted batch {i} → {i + len(batch)}")
def fetch_urls(table_name: str, *args):
    conn = make_connection()
    cursor = conn.cursor()

    try:
        column_string = ", ".join(args) if args else "*"

        query = f"SELECT {column_string} FROM {table_name} where status='pending';"
        cursor.execute(query)

     
        rows = cursor.fetchall()

        print("Rows fetched:", len(rows))

        for row in rows:
            yield row

    except Exception as e:
        print("DB ERROR in fetch_urls:", e)

    finally:
        cursor.close()
        conn.close()#update query
def update_q(tab, column, value):
    conn = make_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            f"UPDATE {tab} SET status=%s WHERE {column}=%s",
            ("responded", value)
        )
        conn.commit()

    except Exception as e:
        print("Update Error:", e)

    finally:
        cursor.close()
        conn.close()