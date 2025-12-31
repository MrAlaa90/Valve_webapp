import os
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_db():
    db_host = os.environ.get('DB_HOST', 'db')
    db_name = os.environ.get('POSTGRES_DB', 'valvedb')
    db_user = os.environ.get('POSTGRES_USER', 'postgres')
    db_password = os.environ.get('POSTGRES_PASSWORD', 'postgres')
    db_port = os.environ.get('DB_PORT', '5432')

    while True:
        try:
            conn = psycopg2.connect(
                host=db_host,
                dbname=db_name,
                user=db_user,
                password=db_password,
                port=db_port
            )
            conn.close()
            print("Database ready!")
            break
        except OperationalError:
            print("Database not ready yet, waiting...")
            time.sleep(1)

if __name__ == '__main__':
    wait_for_db()
