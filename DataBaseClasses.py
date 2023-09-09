import sqlite3


class SQLiteDatabase:
    def __init__(self, db_name):
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"An error occurred while connecting to the database: {e}")
            self.conn = None

    def create_table(self, table_name, columns):
        if not self.conn:
            print("Database connection not available.")
            return
        try:
            query = f'CREATE TABLE IF NOT EXISTS {table_name} ({", ".join(columns)})'
            self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while creating the table: {e}")

    def insert(self, table_name, values):
        if not self.conn:
            print("Database connection not available.")
            return
        try:
            query = f'INSERT INTO {table_name} VALUES ({", ".join(["?" for value in values])})'
            self.cursor.execute(query, values)
            self.conn.commit()
            print("Items inserted", values)
        except sqlite3.Error as e:
            print(f"An error occurred while inserting data: {e}")

    def select(self, table_name, columns, condition=None):
        if not self.conn:
            print("Database connection not available.")
            return
        try:
            query = f'SELECT {", ".join(columns)} FROM {table_name}'
            if condition:
                query += f' WHERE {condition}'
            self.cursor.execute(query)
            return self.cursor.fetchall()

        except sqlite3.Error as e:
            print(f"An error occurred while selecting data: {e}")
            return []

    def update(self, table_name, set_columns, condition=None):
        if not self.conn:
            print("Database connection not available.")
            return
        try:
            query = f'UPDATE {table_name} SET {", ".join([f"{col}=?" for col in set_columns.keys()])}'
            if condition:
                query += f' WHERE {condition} '
            self.cursor.execute(query, list(set_columns.values()))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False
            # print(f"An error occurred while updating data: {e}")

    def delete(self, table_name, condition=None):
        if not self.conn:
            print("Database connection not available.")
            return
        try:
            query = f'DELETE FROM {table_name}'
            if condition:
                query += f' WHERE {condition}'
            self.cursor.execute(query)
            self.conn.commit()
            return "le produit a été supprimé"

        except sqlite3.Error as e:
            return f"Une erreur s'est produite lors de la suppression des données: {e}"

    def close(self):
        if not self.conn:
            print("Database connection not available.")
            return
        self.conn.close()
