import sqlite3
import pandas as pd
import os

DATA_DIR = '/app/data'

class Database:
    def __init__(self, db_name='market_data.db'):
        self.conn = sqlite3.connect(os.path.join(DATA_DIR, db_name))
        self.cursor = self.conn.cursor()

    def create_table(self, table_name):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                symbol TEXT,
                PRIMARY KEY (date, symbol)
            )
        ''')
        self.conn.commit()

    def insert_data(self, table_name, df):
        df.to_sql(table_name, self.conn, if_exists='append', index=False)

    def fetch_data(self, table_name, symbol, start_date, end_date):
        query = f'''
            SELECT * FROM {table_name}
            WHERE symbol = ? AND date BETWEEN ? AND ?
        '''
        return pd.read_sql_query(query, self.conn, params=(symbol, start_date, end_date))

    def close(self):
        self.conn.close()

def load_to_database(asset_type):
    db = Database()
    db.create_table(asset_type)

    processed_dir = os.path.join(DATA_DIR, 'processed', asset_type)
    
    for filename in os.listdir(processed_dir):
        if filename.endswith('.parquet'):
            df = pd.read_parquet(os.path.join(processed_dir, filename))
            symbol = filename.split('_')[0]
            df['symbol'] = symbol
            db.insert_data(asset_type, df)

    db.close()

if __name__ == "__main__":
    load_to_database('stocks')  # You can change this to load different asset types