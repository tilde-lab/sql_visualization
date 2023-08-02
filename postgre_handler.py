import yaml
import psycopg2
from typing import Dict

class PostgreSQL_handler():
    """
    The class gets the necessary information about the database.
    It stores information about tabel names, tabel structures, foreign keys and relationships.
    """
    def __init__(self):
        with open('config.yaml', encoding='utf-8') as f:
            personal_data = yaml.safe_load(f)
        self.conn = self.connection = psycopg2.connect(
        dbname=personal_data["dbname"],
        user=personal_data["user"],
        password=personal_data["password"],
        host=personal_data["host"],
        port=personal_data["port"]
        )
        self.tables = None
        self.tables_structure = {}
        self.connection = None
        self.foreign_keys_for_diagram_builder = {}

    def get_tabel_names(self):
        """
        Func gets informathion about tabel names in db.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = [table[0] for table in cursor.fetchall()]
        self.tables = tables
        print('Table name received successfully.')

    def get_info_about_tables(self):
        """
        Func gets informathion about tabel structures (rows).
        """
        cursor = self.conn.cursor()
        for table in self.tables:
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}';")
            rows = [row[0] for row in cursor.fetchall()]
            self.tables_structure[table] = rows
        print('Table column data has been successfully retrieved')

    def get_info_about_keys(self):
        """
        Func gets information about restrictions on the tables.
        Information about foreign keys and relationships saved in self.connection.
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT 
            tc.table_name AS TABLE_NAME, 
            kcu.column_name AS COLUMN_NAME, 
            tc.constraint_name AS CONSTRAINT_NAME, 
            ccu.table_name AS REFERENCED_TABLE_NAME, 
            ccu.column_name AS REFERENCED_COLUMN_NAME 
            FROM 
            information_schema.table_constraints tc 
            JOIN 
            information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name 
            AND tc.table_schema = kcu.table_schema 
            JOIN 
            information_schema.constraint_column_usage ccu 
            ON ccu.constraint_name = tc.constraint_name 
            AND ccu.table_schema = tc.table_schema 
            WHERE 
            tc.constraint_type = 'FOREIGN KEY';
        """)

        results = cursor.fetchall()

        if results and results != []:
            self.connection = results
            print(f'Keys received successfully. Number of connections established: {len(self.connection)}')
        else:
            print('All tables in the database do not have foreign keys.')
        cursor.close()
        self.conn.close()

    def data_preparation(self):
        """
        This is where information about relationships between tables is processed.
        Finally name of the table and the name of the table associated with it, as well as the keys,
        are saved in self.foreign_keys_for_diagram_builder.
        """
        for tabel in self.tables:
            connection_from_tabel = []
            for relation in self.connection:
                if relation[0] == tabel:
                    connection_from_tabel.append({relation[3]: [relation[1], relation[4]]})
            self.foreign_keys_for_diagram_builder[tabel] = connection_from_tabel

    def start_handler(self) -> Dict:
        """
        Func starts processing data from the database.
        It calls functions step by step to get data about table names, their structure, and foreign keys.
        :return dicts with structure of db and relationships by foreign keys.
        """
        self.get_tabel_names()
        self.get_info_about_tables()
        self.get_info_about_keys()
        self.data_preparation()
        return self.tables_structure, \
            self.foreign_keys_for_diagram_builder


