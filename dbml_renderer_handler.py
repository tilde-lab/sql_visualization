"""
This is one way to build a diagram.

The function generates DBML-code, which is fed to the input of 'dbml-renderer',
which converts to DOT and feeds it to Graphviz. As input, we receive a diagram, which is saved in the folder
'diagram_folder' in png-format.

Using this method, we cannot customize links, chart color, shape, etc. This tool is very limited.
"""
import cairosvg
import subprocess
import os
from datetime import datetime


class DBMLRenderer():
    """
    The class performs the construction of the diagram by dbml-renderer.
    It builds the dbml-code, which will then be passed to the input of the dbml-renderer.
    Unlike PlantUML Builder, the resulting diagram will show data types.
    """
    def __init__(self, db_name: str):
        self.name_db = db_name
        self.date_today = datetime.now().date().strftime('%Y-%m-%d')
        self.construction_stage = {}
        self.numeric_of_conn = {}

    def define_column_type(self, column_types: dict, tabel: str, column: str) -> str:
        """
        Func is define type of specific column.
        """
        data_for_tabel = column_types[tabel]
        type_for_column = data_for_tabel[column]
        type_for_column = type_for_column.replace(' ', '_')
        type_for_column = type_for_column.replace('-', '_')
        return type_for_column

    def calculate_number_of_links(self, communication):
        """
        Here the number of links in each table is calculated.
        """
        for t_f in list(communication.keys()):
            self.numeric_of_conn[t_f] = len(communication[t_f])

        for t_f in list(communication.keys()):
            if communication[t_f] != []:
                for conn in communication[t_f]:
                    self.numeric_of_conn[list(conn.keys())[0]] += 1

    def constructor_handler(
            self, tables_structure: dict, foreign_keys_for_diagram_builder: dict, primary_keys: dict, column_types: dict
    ) -> str:
        """
        Func creates dbml-code.
        It handles data about tabel and return code for dbml-renderer.
        """
        self.calculate_number_of_links(foreign_keys_for_diagram_builder)
        dbml_code = ""
        # Creates code with information about tables structure.
        for tabel in tables_structure.keys():
            if self.numeric_of_conn[tabel] > 0:
                tabel_code = f"Table {tabel} "+"{\n"
                for column in tables_structure[tabel]:
                    column_type = self.define_column_type(column_types, tabel, column)
                    if column in primary_keys[tabel]:
                        tabel_code += f'{column} {column_type} [primary key]\n'
                    else:
                        tabel_code += f'{column} {column_type}\n'
                tabel_code += '}\n\n'
                dbml_code += tabel_code

        # Creates code with information about connections between tables.
        for tabel_from in foreign_keys_for_diagram_builder.keys():
            for conn_info in foreign_keys_for_diagram_builder[tabel_from]:
                tabel_to = list(conn_info.keys())[0]
                key_from = conn_info[tabel_to][0]
                key_to = conn_info[tabel_to][1]

                # FIXME: not implemented direction.
                direction = self.block_allocation(foreign_keys_for_diagram_builder, tabel_from, tabel_to)
                if direction:
                    conn_code = f"Ref: {tabel_from}.{key_from} > {tabel_to}.{key_to}\n"
                else:
                    conn_code = f"Ref: {tabel_to}.{key_to} < {tabel_from}.{key_from}\n"
                if conn_code not in dbml_code:
                    dbml_code += conn_code
        return dbml_code

    def block_allocation(self, communication: dict, tabel_from: str, tabel_to) -> bool:
        """
        Func decides on the order in which related blocks are placed.
        return: bool.
        """
        print(tabel_from, tabel_to)
        if tabel_from not in self.construction_stage or tabel_to not in self.construction_stage:
            if tabel_from not in self.construction_stage and tabel_to not in self.construction_stage:
                self.construction_stage[tabel_from] = 1
                self.construction_stage[tabel_to] = 1
            if tabel_from not in self.construction_stage:
                self.construction_stage[tabel_from] = 1
                self.construction_stage[tabel_to] += 1
            if tabel_to not in self.construction_stage:
                self.construction_stage[tabel_to] = 1
                self.construction_stage[tabel_from] += 1
        else:
            self.construction_stage[tabel_from] += 1
            self.construction_stage[tabel_to] += 1
        # если tabel_from многосвязный
        if self.numeric_of_conn[tabel_from] > 4 and self.numeric_of_conn[tabel_to] <= 4:

            # communication will do from right to left.
            if self.numeric_of_conn[tabel_from] // 2 < self.construction_stage[tabel_from]:
                return False
            # communication will do from left to right.
            else:
                return True

            # если tabel_to многосвязный
        elif self.numeric_of_conn[tabel_to] > 4:
            # communication will do from right to left.
            if self.numeric_of_conn[tabel_to] // 2 < self.construction_stage[tabel_to]:
                return True
            # communication will do from left to right.
            else:
                return False
        else:
            return True

    def save_dbml_folder(self, dbml_code: str):
        """
        Func saves dbml file.
        """
        with open(r"demo.dbml", "w") as f:
            f.write(dbml_code)

    def create_diagram_handler(self) -> bool:
        """
        Func executes a command in the console that creates a diagram in svg-format.
        Converts to jpg-format, added white background.
        """
        answer = False
        if not os.path.exists('diagram_folder'):
            os.makedirs('diagram_folder')

        command_line = r"dbml-renderer.cmd -i demo.dbml -o demo.svg"
        try:
            subprocess.run(command_line)
        except:
            print("Failed to start 'dbml-renderer'.")
            return
        else:
            print("Successfully launched 'dbml-renderer'.")

        while answer == False:
            try:
                answer = cairosvg.svg2png(
                    url=r'demo.svg',
                    write_to=f'./diagram_folder/{self.name_db}_{self.date_today}.jpg', background_color="#FFFFFF"
                )
            except:
                continue
        return True

    def delete_dbml_code_file(self):
        """
        Func is delete file with dbml-code.
        """
        os.remove(r'demo.dbml')
        os.remove(r'demo.svg')

    def start_handler(
            self, tables_structure, foreign_keys_for_diagram_builder, primary_keys, column_types
    ):
        """
        Performs the functions of creating diagrams.
        """
        dbml_code = self.constructor_handler(
            tables_structure, foreign_keys_for_diagram_builder, primary_keys, column_types
        )
        self.save_dbml_folder(dbml_code)
        if self.create_diagram_handler():
            self.delete_dbml_code_file()


