"""
This is where the diagram is being constructed.

The PlantUML tool is used to create the diagram.
It allows the use of a simpler DSL markup language. The DSL code is input to the PlantUML executable file,
then it independently translates this code into the DOT language and sends it to Graphiz.
Graphiz independently builds a diagram based on the requirements in the code.
"""
import subprocess
import yaml
import random

class DiagramBuilder():
    """
    The class performs data processing about db. Builds a chart based on this data.
    Its main task is to describe the code (diagram structure) in the DSL language.
    """
    def __init__(self):
        with open('config.yaml', encoding='utf-8') as f:
            personal_data = yaml.safe_load(f)
        self.path_to_plantuml = personal_data['path_plantuml']
        self.db_name = personal_data['dbname']
        self.keys_to_bold = []
        self.colors_for_link = [r'[#b8005f]', r'[#04c73b]', r'[#0508e3]', \
                                r'[#eb8c10]', r'[#10d1eb]', r'[#fa2a70]', \
                                '[#ed0000]', '[#000d0d]']

    def constructor(
            self, tables: dict, communication: dict, keys_in_table:
            dict, number_of_keys: dict, primary_key: dict
    ) -> str:
        """
        Func includes code development for plotting charts.
        tables: dict with name of the tables, name of column.
        communication: dict with data about relationships between tables.
        """
        tables_code = ''
        communication_code = ''
        for t in tables.keys():
            columns = tables[t]
            columns_code = ''
            for idx, column in enumerate(columns):
                if t in primary_key:
                    # Checking that the column is a primary key. If yes: title will be bold.
                    if column in primary_key[t]:
                        columns_code += f'**{column}**\n' + '..\n'
                        continue
                # Checking that the table is in the dictionary where information about the foreign keys is stored.
                if t in keys_in_table:
                    # Checking that the column is a foreign key. If yes: title will be bold.
                    if column in keys_in_table[t]:
                        if idx + 1 != len(columns):
                            columns_code += f'**{column}**\n' + '..\n'
                        else:
                            columns_code += f'**{column}**\n' + '..\n'
                    else:
                        columns_code += f'{column}\n' + '..\n'
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
        for table_from in number_of_keys:
            connection = ''
            for table_to in communication[table_from]:
                table_to = table_to.items()
                first_item = list(table_to)[0]
                name_of_finish_table = first_item[0]
                key_from_start_table = (first_item[1])[0]
                key_from_finish_table = (first_item[1])[1]

                if (name_of_finish_table, table_from) not in done_tabel:
                    color = color_for_keys[(table_from, key_from_start_table)]
                    relation = \
                        f'{table_from}::{key_from_start_table} --{color}' \
                        f' {name_of_finish_table}::{key_from_finish_table}\n'
                    connection += relation
                    done_tabel.append((table_from, name_of_finish_table))
            communication_code += connection
        uml_code = '@startuml\n' \
                   'left to right direction' \
                   + f'\n{tables_code}\n' \
                   + f'{communication_code}\n' \
                     '@enduml'
        return uml_code

    def link_color_selection(self, communication) -> dict:
        """
        Func selects the color for the link between two tabels.
        Each key has its own color.
        At a certain scale, the colors of links can be repeated.
        :return: dict ((tabel, key ): color).
        """
        colors = {}
        for tabel_from in communication:
            connects = communication[tabel_from]
            for tabel_info in connects:
                tabel_to = list(tabel_info.keys())[0]
                keys = tabel_info[tabel_to]
                if (tabel_from, keys[0]) not in colors and (tabel_to, keys[1]) not in colors:
                    color = random.choice(self.colors_for_link)
                    colors[(tabel_from, keys[0])] = color
                    colors[(tabel_to, keys[1])] = color
                    if len(self.colors_for_link) > 2:
                        self.colors_for_link.remove(color)
                elif (tabel_from, keys[0]) not in colors and (tabel_to, keys[1]) in colors:
                    colors[(tabel_from, keys[0])] = colors[(tabel_to, keys[1])]
                elif (tabel_from, keys[0]) in colors and (tabel_to, keys[1]) not in colors:
                    colors[(tabel_to, keys[1])] = colors[(tabel_from, keys[0])]
        return colors

    def save_uml_code(self, uml_code: str, scale=3) -> None:
        """
        Func save uml-code in txt format.
        scale: image quality index. Optimal: 2 or 3.
        """
        uml_code = uml_code.replace("@startuml", f"@startuml\nscale {scale}\n")
        with open(f"{self.db_name}.txt", "w") as f:
            f.write(uml_code)

    def build_diagram(self):
        """
        Func is performing the construction of a diagram using PlantUML.
        The diagram is saved in png format.
        """
        subprocess.call(["java", "-jar", self.path_to_plantuml, f"{self.db_name}.txt", "-tpng"])




