from datetime import datetime
import os
import subprocess

class Graphviz_handler():
    def __init__(self, db_name: str):
        self.name_db = db_name
        self.date_today = datetime.now().date().strftime('%Y-%m-%d')
        self.construction_stage = {}
        self.numeric_of_conn = {}

    def dot_constructor(
            self, tables_structure, foreign_keys_for_diagram_builder,
            keys_in_table, primary_keys, direction_default
    ):
        dot_code = 'digraph G { \n' \
        'node[shape = none, margin = 0]\n' \
        'edge[arrowtail = none, dir = both]\n'
        dot_code += self.dot_tables(tables_structure, primary_keys)
        dot_code += self.dot_links(foreign_keys_for_diagram_builder)
        dot_code += '\n}'
        return dot_code

    def dot_links(self, foreign_keys_for_diagram_builder):
        links_code = ''
        for table_from in foreign_keys_for_diagram_builder.keys():
            for conn_info in foreign_keys_for_diagram_builder[table_from]:
                tabel_to = list(conn_info.keys())[0]
                key_from = conn_info[tabel_to][0]
                key_to = conn_info[tabel_to][1]
                conn_code = f"{table_from.title()}:{key_from} -> {tabel_to.title()}:{key_to};\n"
                if conn_code not in links_code:
                    links_code += conn_code
        return links_code

    def dot_tables(self, tables_structure, primary_keys) -> str:
        code = ""
        for table in tables_structure.keys():
            code += f'{table.title()} [label=< \n' \
            '<table border="0" cellborder="1" cellspacing="0" cellpadding="4"> \n' \
            f'<tr><td bgcolor="lightblue">{table.title()}</td></tr> \n'
            rows = ''
            columns = tables_structure[table]
            for column in columns:
                rows += f'<tr><td align="left" port="{column}">{column}</td></tr>\n'
            rows += '</table>\n>]\n\n'
            code += rows
        return code

    def save_dot(self, dot_code):
        with open(r"demo.dot", "w") as f:
            f.write(dot_code)

    def diagram_bilder(self):
        if not os.path.exists('diagram_folder'):
            os.makedirs('diagram_folder')

        cmd = r'dot -Tpng demo.dot -o output.png'
        subprocess.run(cmd)

    def delete_dot(self):
        os.remove(r'demo.dot')

    def start_handler(
            self, tables_structure: dict, foreign_keys_for_diagram_builder: dict,
            keys_in_table: dict, primary_keys: dict, direction_default: str
    ):
        dot_code = self.dot_constructor(
            tables_structure, foreign_keys_for_diagram_builder, keys_in_table, primary_keys, direction_default
        )
        self.save_dot(dot_code)
        self.diagram_bilder()

