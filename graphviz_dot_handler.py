"""
This way generates a diagram using Graphviz-only.
The file is constructed in DOT format and transferred to Graphviz.
"""
from datetime import datetime
import os
import subprocess
from saver import Saver


class Graphviz_handler():
    """
    The class performs the construction of the diagram by Graphviz.
    It builds DOT-code with which contains the markup for the diagram.
    """
    def __init__(self, db_name: str, output_path: str):
        self.name_db = db_name
        self.date_today = datetime.now().date().strftime('%Y-%m-%d')
        self.construction_stage = {}
        self.numeric_of_conn = {}
        self.output_path = output_path
        self.img_name = f'{self.name_db}_{self.date_today}.png'
        self.saver = Saver(self.output_path, self.img_name)

    def dot_constructor(
            self, tables_structure: dict, foreign_keys_for_diagram_builder: dict,
            primary_keys: dict
    ) -> str:
        """
        This is where the DOT-code is assembled.
        """
        self.calculate_number_of_links(foreign_keys_for_diagram_builder)
        dot_code = 'digraph G { \n' \
        'node[shape = none, margin = 0]\n' \
        'edge[arrowtail = none]\n'
        dot_code += self.dot_tables(tables_structure, primary_keys)
        dot_code += self.dot_links(foreign_keys_for_diagram_builder)
        dot_code += '\n}'
        return dot_code


    def dot_links(self, foreign_keys_for_diagram_builder: dict) -> str:
        """
        This is where links between tables are established.
        """
        links_code = 'rankdir=LR;\n'
        for table_from in foreign_keys_for_diagram_builder.keys():
            for conn_info in foreign_keys_for_diagram_builder[table_from]:
                tabel_to = list(conn_info.keys())[0]
                key_from = conn_info[tabel_to][0]
                key_to = conn_info[tabel_to][1]
                dir = self.block_allocation(table_from, tabel_to)
                if dir:
                    conn_code = f"{table_from.title()}:{key_from} -> {tabel_to.title()}:{key_to} [dir=none];\n"
                else:
                    conn_code = f"{tabel_to.title()}:{key_to} -> {table_from.title()}:{key_from} [dir=none];\n"
                if conn_code not in links_code:
                    links_code += conn_code
        return links_code

    def dot_tables(self, tables_structure: dict, primary_keys: dict) -> str:
        """
        This is where markup for tables is created.
        """
        code_for_all_tabels = ""
        for table in tables_structure.keys():
            code = f'{table.title()} [label=< \n' \
            '<table border="0" cellborder="1" cellspacing="0" cellpadding="4"> \n' \
            f'<tr><td bgcolor="lightblue">{table.title()}</td></tr> \n'
            rows = ''
            columns = tables_structure[table]
            for column in columns:
                # primary keys is bold.
                if column in primary_keys[table]:
                    rows += f'<tr><td align="left" port="{column}"><b>{column}</b></td></tr>\n'
                else:
                    rows += f'<tr><td align="left" port="{column}">{column}</td></tr>\n'
            rows += '</table>\n>]\n\n'
            code += rows
            code_for_all_tabels += code

        return code_for_all_tabels

    def linear_position_distribution(self, tables_structure: dict) -> str:
        if len(tables_structure.keys()) < 10:
            coef = 3
        elif 16 >= len(tables_structure.keys()) >= 10:
            coef = 4
        else:
            coef = 5
        code = ''
        code_for_row = '{ rank = same; '
        cnt = 1
        for table in tables_structure.keys():
            cnt += 1
            code_for_row += f'"{table.title()}"; '
            if cnt == coef:
                code_for_row += '}\n'
                code += code_for_row
                code_for_row = '{ rank = same; '
                cnt = 1
        return code

    def block_allocation(self, table_from: str, tabel_to) -> bool:
        """
        Func decides on the order in which related blocks are placed.
        return: bool.
        """
        if table_from not in self.construction_stage or tabel_to not in self.construction_stage:
            if table_from not in self.construction_stage and tabel_to not in self.construction_stage:
                self.construction_stage[table_from] = 1
                self.construction_stage[tabel_to] = 1
            if table_from not in self.construction_stage:
                self.construction_stage[table_from] = 1
                self.construction_stage[tabel_to] += 1
            if tabel_to not in self.construction_stage:
                self.construction_stage[tabel_to] = 1
                self.construction_stage[table_from] += 1
        else:
            self.construction_stage[table_from] += 1
            self.construction_stage[tabel_to] += 1
        # если table_from многосвязный
        if self.numeric_of_conn[table_from] > 4 and self.numeric_of_conn[tabel_to] <= 4:

            # communication will do from right to left.
            if self.numeric_of_conn[table_from] // 2 < self.construction_stage[table_from]:
                return False
            # communication will do from left to right.
            else:
                return True

    def save_dot(self, dot_code: str):
        """
        This is where the markup is saved in DOT-format.
        """
        with open(r"demo.dot", "w") as f:
            f.write(dot_code)

    def diagram_bilder(self):
        """
        Diagram in progress by Graphviz.
        """
        if not os.path.exists('diagram_folder'):
            os.makedirs('diagram_folder')

        cmd = [
            'dot', 
            '-Tpng', 
            'demo.dot', 
            '-o', 
            os.path.join("./diagram_folder", f'{self.name_db}_{self.date_today}.png')
        ]

        try:
            subprocess.run(cmd, check=True)
        except:
            print("Failed to start 'dot-renderer'.")
        else:
            if self.output_path:
                self.saver.save()
                print("Successfully launched 'dot-renderer'.")
            else:
                print("Successfully launched 'dot-renderer'.")

    def delete_dot(self):
        os.remove(r'demo.dot')

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

    def start_handler(
            self, tables_structure: dict, foreign_keys_for_diagram_builder: dict,
            primary_keys
    ):
        """
        Calls functions for rendering the diagram.
        """
        dot_code = self.dot_constructor(
            tables_structure, foreign_keys_for_diagram_builder, primary_keys
        )
        self.save_dot(dot_code)
        self.diagram_bilder()
        self.delete_dot()

