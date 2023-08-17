import psycopg2
from psycopg2 import Error
from typing import Dict
from eralchemy import render_er
import os
from datetime import datetime

class PostgreSQL_handler():
    """
    The class gets the necessary information about the database.
    It stores information about tabel names, tabel structures, foreign keys and relationships.
    """
    def __init__(self, host, port, user, password, db_name, schema_name):
        try:
            self.conn = self.connection = psycopg2.connect(
                dbname=db_name, user=user, password=password, host=host, port=port
            )
        except Error as e:
            print(f"{e}")

        self.schema = schema_name
        self.tables = []
        self.tables_structure = {}
        self.connection = None
        self.foreign_keys = {}
        self.primary_keys = {}
        self.keys_in_table = {}
        self.number_of_keys = {}
        self.column_types = {}

    def check_schema_names(self):
        """
        Checks if the schema exists in db.
        """
        try:
            cursor = self.conn.cursor()
        except:
            print(f'Error connecting to the database, please check your personal data.')
            return False
        else:
            cursor.execute("SELECT schema_name \
                            FROM information_schema.schemata \
                            WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema';")
            schemas = [table[0] for table in cursor.fetchall()]
            if self.schema in schemas:
                return True
            else:
                print(f'The selected schema does not exist.')
                return False

    def get_tabel_names(self) -> bool:
        """
        Func gets informathion about tabel names in db.
        """

        cursor = self.conn.cursor()

        # Ignore virtual tables (view).
        cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{self.schema}' " 
                       f"AND table_type = 'BASE TABLE';")
        tables = [table[0] for table in cursor.fetchall()]
        if tables != []:
            [self.tables.append(table) for table in tables]
            print('Table name received successfully.')
            return True
        else:
            print('Attention! In db not tables.')
            return False

    def get_info_about_tables(self) -> bool:
        """
        Func gets informathion about tabel structures (columns).
        """
        cursor = self.conn.cursor()
        for table in self.tables:
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}';")
            columns = [column[0] for column in cursor.fetchall()]
            self.tables_structure[table] = columns
        cursor.close()
        if self.tables_structure != {}:
            print('Table column data has been successfully retrieved.')
            return True
        else:
            print('In tables not columns at all.')
            return False

    def get_info_about_foreign_keys(self):
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
            keys = []
            for el in results:
                if el not in keys:
                    keys.append(el)
            self.connection = keys
            print(f'Keys received successfully. Number of connections established: {len(self.connection)}.')
        else:
            print('All tables in the database do not have foreign keys.')
        cursor.close()

    def get_info_about_primary_keys(self):
        cursor = self.conn.cursor()
        for tabel in self.tables:
            # a.attname - name of columns, pg_index - system table;
            # Join two tables: pg_attribute and pg_attribute, by attrelid (identifier).
            cursor.execute(f"""
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = '"{self.schema}"."{tabel}"'::regclass AND i.indisprimary;
            """)

            results = cursor.fetchall()

            if results != []:
                primary_keys = [i[0] for i in results]
                self.primary_keys[tabel] = primary_keys

        if self.primary_keys == {}:
            print('Tables do not have primary keys.')

    def data_preparation(self):
        """
        This is where information about relationships between tables is processed.
        Finally name of the table and the name of the table associated with it, as well as the keys,
        are saved in self.foreign_keys.
        """
        for table in self.tables:
            connection_from_tabel = []
            if self.connection:
                for relation in self.connection:
                    if relation[0] == table:
                        connection_from_tabel.append({relation[3]: [relation[1], relation[4]]})
                self.foreign_keys[table] = connection_from_tabel

                for relation in self.connection:
                    first_table = relation[0]
                    first_key = relation[1]
                    second_table = relation[3]
                    second_key = relation[4]
                    if first_table in self.keys_in_table:
                        if first_key not in self.keys_in_table[first_table]:
                            self.keys_in_table[first_table].append(first_key)
                    else:
                        self.keys_in_table[first_table] = [first_key]
                    if second_table in self.keys_in_table:
                        if second_key not in self.keys_in_table[second_table]:
                            self.keys_in_table[second_table].append(second_key)
                    else:
                        self.keys_in_table[second_table] = [second_key]

                for table in list(self.keys_in_table.items()):
                    self.number_of_keys[table[0]] = len(table[1])

    def get_column_types(self):
        """
        Func gets info about type of column in tables.
        """
        cursor = self.conn.cursor()
        for tabel in self.tables:
            cursor.execute(f" \
                SELECT column_name, data_type \
                FROM information_schema.columns \
                WHERE table_name = '{tabel}' \
            ")
            results = cursor.fetchall()
            tabel_data = {}
            if results != []:
                for column_data in results:
                    column = column_data[0]
                    type_c = column_data[1]
                    tabel_data[column] = type_c
                self.column_types[tabel] = tabel_data

    def start_handler(self) -> Dict:
        """
        Func starts processing data from the database.
        It calls functions step by step to get data about table names, their structure, and foreign keys.
        return: dicts with structure of db and relationships by foreign keys.
        """
        if self.check_schema_names():
            answer = self.get_tabel_names()
            if answer:
                get_columns = self.get_info_about_tables()
                if get_columns:
                    self.get_column_types()
                    self.get_info_about_foreign_keys()
                    self.get_info_about_primary_keys()
                    self.data_preparation()
                    return self.tables_structure, \
                        self.foreign_keys, \
                        self.keys_in_table, \
                        dict(sorted(self.number_of_keys.items(), key=lambda item: item[1], reverse=True)), \
                        self.primary_keys, \
                        self.column_types
            else:
                return False
        else:
            return False


class ERAlchemyHandler():
    """
    Class performs building diagram by 'ERAlchemy'.
    It accesses an existing table by path and builds a diagram.
    Unlike other methods, it does not need to provide ready-made data.
    """
    def __init__(self, db_name: str, user_name: str, password: str, host: str):
        self.name_db = db_name
        self.user_name = user_name
        self.password = password
        self.host = host
        self.date_today = datetime.now().date().strftime('%Y-%m-%d')

    def start_handler(self):
        if not os.path.exists('diagram_folder'):
            os.makedirs('diagram_folder')

        url = f'postgresql://{self.user_name}:{self.password}@{self.host}/{self.name_db}'
        output_path = f'./diagram_folder/{self.name_db}_{self.date_today}_.png'
        render_er(url, output_path)



