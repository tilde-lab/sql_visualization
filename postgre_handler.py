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
        self.schema = []
        self.tables = []
        self.tables_structure = {}
        self.connection = None
        self.foreign_keys = {}
        self.primary_keys = {}
        self.keys_in_table = {}
        self.number_of_keys = {}

    def get_schema_names(self):
        """
        Func gets informathion about schema names in db.
        Ignore 'information_schema'.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT schema_name \
                        FROM information_schema.schemata \
                        WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema';")
        schema = [table[0] for table in cursor.fetchall()]
        self.schema = schema
        print(f'Found schemas in the database: {len(schema)}')

    def get_tabel_names(self) -> bool:
        """
        Func gets informathion about tabel names in db.
        """
        tabels_in_schema = {}
        for schema in self.schema:
            cursor = self.conn.cursor()

            # Ignore virtual tables (view)
            cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}' " 
                           f"AND table_type = 'BASE TABLE';")
            tables = [table[0] for table in cursor.fetchall()]
            if tables != []:
                [self.tables.append(table) for table in tables]
                tabels_in_schema[schema] = tables
        if tabels_in_schema != {}:
            self.schema = tabels_in_schema
        if tables != []:
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
            print('Table column data has been successfully retrieved')
            return True
        else:
            print('In tables not columns at all.')
            return False

    def get_info_about_foriegn_keys(self):
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

    def get_info_about_primary_keys(self):
        cursor = self.conn.cursor()
        for schema in self.schema.keys():
            for tabel in self.tables:
                # a.attname - name of columns, pg_index - system table;
                # Join two tables: pg_attribute and pg_attribute, by attrelid (identifier).
                cursor.execute(f"""
                    SELECT a.attname
                    FROM pg_index i
                    JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                    WHERE i.indrelid = '{schema}.{tabel}'::regclass AND i.indisprimary;
                """)

                results = cursor.fetchall()

                if results != []:
                    primary_keys = [i[0] for i in results]
                    self.primary_keys[tabel] = primary_keys
            else:
                continue

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

    def start_handler(self) -> Dict:
        """
        Func starts processing data from the database.
        It calls functions step by step to get data about table names, their structure, and foreign keys.
        :return dicts with structure of db and relationships by foreign keys.
        """
        self.get_schema_names()
        answer = self.get_tabel_names()
        if answer:
            get_columns = self.get_info_about_tables()
            if get_columns:
                self.get_info_about_foriegn_keys()
                self.get_info_about_primary_keys()
                self.data_preparation()
                return self.tables_structure, \
                    self.foreign_keys, \
                    self.keys_in_table, \
                    dict(sorted(self.number_of_keys.items(), key=lambda item: item[1], reverse=True)), \
                    self.primary_keys
        else:
            return False


