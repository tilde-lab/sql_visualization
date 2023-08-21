"""
This is where the diagram is being constructed.

The PlantUML tool is used to create the diagram.
It allows the use of a simpler DSL markup language. The DSL code is input to the PlantUML executable file,
then it independently translates this code into the DOT language and sends it to Graphviz.
Graphviz independently builds a diagram based on the requirements in the code.
"""
import subprocess
from datetime import datetime
import os
import shutil


class PlantUMLBilder():
    """
    The class performs data processing about db. Builds a chart based on this data.
    Its main task is to describe the code (diagram structure) in the DSL language.
    """
    def __init__(self, db_name, output_path):
        self.construction_stage = {}
        self.date_today = datetime.now().date().strftime('%Y-%m-%d')
        self.path_to_plantuml = "third_party/plantuml.jar"
        self.db_name = db_name
        self.keys_to_bold = []
        self.numeric_of_conn = {}
        self.output_path = output_path
        # bold version.
        self.colors_for_link = [r'[#f51505,bold]', r'[#877951,bold]', r'[#0057f7,bold]',
                                r'[#21a105,bold]', r'[#eb8b05,bold]', r'[#d005eb,bold]',
                                r'[#b80263,bold]', r'[#0091a1,bold]', r'[#00a173,bold]',
                                r'[#7815cf,bold]', r'[#afb500,bold]', r'[#cf6967,bold]']

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

    def constructor(
            self, tables: dict, communication: dict, keys_in_table:
            dict, primary_key: dict, direction_default: str
    ) -> str:
        """
        Func includes code development for plotting diagram.
        tables: dict with name of the tables, name of column.
        communication: dict with data about relationships between tables.
        keys_in_table: dict with foreign key names.
        primary_key: dict with primary key names.
        """
        tables_code = ''
        communication_code = ''
        self.calculate_number_of_links(communication)

        for t in tables.keys():
            columns = tables[t]
            columns_code = ''
            for idx, column in enumerate(columns):
                if t in primary_key:
                    # Checking that the column is a primary key. If yes: title will be bold.
                    if column in primary_key[t]:
                        if idx + 1 != len(columns):
                            columns_code += f'**{column}**\n' + '..\n'
                            continue
                        else:
                            columns_code += f'**{column}**\n'
                            continue
                # Checking that the table is in the dictionary where information about the foreign keys is stored.
                if t in keys_in_table:
                    # Checking that the column is a foreign key. If yes: title will be bold.
                    if column in keys_in_table[t]:
                        if idx + 1 != len(columns):
                            columns_code += f'**{column}**\n' + '..\n'
                        else:
                            columns_code += f'**{column}**\n'
                    else:
                        if idx + 1 != len(columns):
                            columns_code += f'{column}\n' + '..\n'
                        else:
                            columns_code += f'{column}\n'
                else:
                    if idx + 1 != len(columns):
                        columns_code += f'{column}\n' + '..\n'
                    else:
                        columns_code += f'{column}\n'
            table_code = f'class {t} << (T, transparent) >>' + '{\n' \
                                                               f'{columns_code} \n' \
                                                               '}\n'
            tables_code += table_code

        color_for_keys = self.link_color_selection(communication)
        done_tabel = []

        for table_from in communication.keys():
            for conn_inform in communication[table_from]:
                connection = ''
                conn_inform = list(conn_inform.items())[0]
                tabel_to = conn_inform[0]
                key_from_start = (conn_inform[1])[0]
                key_from_finish = (conn_inform[1])[1]

                if (table_from, key_from_start, key_from_finish, tabel_to) not in done_tabel:
                    color = color_for_keys[(table_from, key_from_start)]
                    # if direction_default = '2' is selected, then all links will be from left to right.
                    if direction_default == "2":
                        from_left_to_right = self.block_allocation_by_key(communication, table_from)
                    else:
                        from_left_to_right = self.block_allocation(table_from, tabel_to)
                    if from_left_to_right:
                        relation = \
                            f' {table_from}::{key_from_start} --{color}' \
                            f' {tabel_to}::{key_from_finish}\n'
                    else:
                        relation = \
                            f'{tabel_to}::{key_from_finish} --{color}' \
                            f' {table_from}::{key_from_start}\n'
                    if relation not in connection and relation not in communication_code:
                        connection += relation
                        communication_code += connection

        uml_code = '@startuml\n' \
                   '!define ClassFontName "Arial"\n\n' \
                   'hide circle\n'\
                   'left to right direction\n' \
                   + f'\n{tables_code}\n' \
                   + f'{communication_code}\n' \
                   + f'remove @unlinked\n' \
                     '@enduml'
        return uml_code

    def block_allocation_by_key(self, communication: dict, tabel_from: str) -> bool:
        """
        Affects the layout of tables.
        Determines the location based on the number of relationships from a particular key.
        """
        data_about_communication = communication[tabel_from]
        if len(data_about_communication) > 4:
            if tabel_from not in self.construction_stage:
                self.construction_stage[tabel_from] = 1
                return True
            else:
                self.construction_stage[tabel_from] += 1
                # communication will do from right to left.
                if len(data_about_communication) // 2 < self.construction_stage[tabel_from]:
                    return False
                # communication will do from left to right.
                else:
                    return True
        else:
            return True

    def together_allocation(self, communication) -> str:
        """
        Can implement block grouping.
        """
        code = '\n\ntogether {'
        for tabel in communication.keys():
            if self.numeric_of_conn[tabel] == 0:
                code += f'\nclass {tabel}'
        if code != '':
            for tabel in communication.keys():
                if self.numeric_of_conn[tabel] == max(self.numeric_of_conn.values()):
                    code += f'\nclass {tabel}\n'
            code += '}\n'
            return code

    def block_allocation(self, tabel_from: str, tabel_to) -> bool:
        """
        Func decides on the order in which related blocks are placed.
        Determines the location based on the number of relationships from specific table.
        return: bool.
        """
        # Add stage of implemented link for tracking in next.
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

        # if 'tabel_from' have a lot of links
        if self.numeric_of_conn[tabel_from] > 2 and self.numeric_of_conn[tabel_to] <= 3:

            # communication will do from right to left.
            if self.numeric_of_conn[tabel_from] // 2 < self.construction_stage[tabel_from]:
                return False
            # communication will do from left to right.
            else:
                return True

            # if 'tabel_to' have a lot of links
        elif self.numeric_of_conn[tabel_to] > 2:
            # communication will do from right to left.
            if self.numeric_of_conn[tabel_to] // 2 < self.construction_stage[tabel_to]:
                return True
            # communication will do from left to right.
            else:
                return False
        else:
            return True

    def link_color_selection(self, communication) -> dict:
        """
        Func selects the color for the link between two tables.
        Each key has its own color.
        At a certain scale, the colors of links can be repeated.
        :return: dict ((tabel, key): color).
        """
        colors = {}
        for tabel_from in communication:
            connects = communication[tabel_from]
            for tabel_info in connects:
                tabel_to = list(tabel_info.keys())[0]
                keys = tabel_info[tabel_to]
                if (tabel_from, keys[0]) not in colors and (tabel_to, keys[1]) not in colors:
                    color = self.colors_for_link[0]
                    colors[(tabel_from, keys[0])] = color
                    colors[(tabel_to, keys[1])] = color
                    if len(self.colors_for_link) > 1:
                        self.colors_for_link.remove(color)
                elif (tabel_from, keys[0]) not in colors and (tabel_to, keys[1]) in colors:
                    colors[(tabel_from, keys[0])] = colors[(tabel_to, keys[1])]
                elif (tabel_from, keys[0]) in colors and (tabel_to, keys[1]) not in colors:
                    colors[(tabel_to, keys[1])] = colors[(tabel_from, keys[0])]
        return colors

    def save_uml_code(self, uml_code: str, tables_structor) -> None:
        """
        Func save uml-code in txt format.
        scale: image quality index.
        Optimal scale: 2 (if more than 10 tables in db) or 3 (if less than 10 tables in db).
        """
        if len(list(tables_structor.keys())) < 11:
            scale = 3
        elif 21 > len(list(tables_structor.keys())) > 10:
            scale = 2
        else:
            scale = 1
        uml_code = uml_code.replace("@startuml", f"@startuml\nscale {scale}\n")
        with open(f"{self.db_name}__{self.date_today}.txt", "w") as f:
            f.write(uml_code)

    def build_diagram(self):
        """
        Func is performing the construction of a diagram using PlantUML.
        The diagram is saved with png format in 'diagram_folder'.
        """
        if not os.path.exists('diagram_folder'):
            os.makedirs('diagram_folder')

        subprocess.call(["java", "-jar", self.path_to_plantuml,
                                 f"{self.db_name}__{self.date_today}.txt", f"-o{'diagram_folder'}", "-tpng"])
        if self.output_path:
            try:
                shutil.move(f'./diagram_folder/{self.db_name}__{self.date_today}.png', self.output_path)
            except:
                print(f'"{self.db_name}__{self.date_today}.png" already exists')

    def delete_uml_code_file(self):
        """
        Func is delete file with uml-code.
        """
        os.remove(f'./{self.db_name}__{self.date_today}.txt')

    def start_handler(
            self, tables_structure: dict, foreign_keys_for_diagram_builder: dict,
            keys_in_table: dict, primary_keys: dict, direction_default: str
    ):
        """
        Start building a diagram based on data about the database.
        """
        uml_code = self.constructor(
            tables_structure, foreign_keys_for_diagram_builder, keys_in_table, primary_keys, direction_default
        )
        self.save_uml_code(uml_code, tables_structure)
        self.build_diagram()
        self.delete_uml_code_file()
        print("Successfully launched 'PlantUMLBilder'.")





