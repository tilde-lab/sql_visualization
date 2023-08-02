"""
This is where the diagram is being constructed.

The PlantUML tool is used to create the diagram.
It allows the use of a simpler DSL markup language. The DSL code is input to the PlantUML executable file,
then it independently translates this code into the DOT language and sends it to Graphiz.
Graphiz independently builds a diagram based on the requirements in the code.
"""
import subprocess
import yaml

class DiagramBuilder():
    """
    The class performs data processing about db. Builds a chart based on this data.
    Its main task is to describe the code (diagram structure) in the DSL language.
    """
    def __init__(self, db_name: str):
        with open('config.yaml', encoding='utf-8') as f:
            personal_data = yaml.safe_load(f)
        self.path_to_plantuml = personal_data['path_plantuml']
        self.db_name = db_name

    def constructor(self, tables: dict, communication: dict) -> str:
        """
        Func includes code development for plotting charts.
        tables: dict with name of the tables, name of rows.
        communication: dict with data about relationships between tables.
        """
        tables_code = ''
        communication_code = ''
        for t in tables.keys():
            rows = tables[t]
            rows_code = ''
            for row in rows:
                rows_code += f'{row}\n'
            table_code = f'class {t} << (T, orchid) >>'+'{\n' \
                         f'{rows_code} \n' \
                         '}\n'
            tables_code += table_code
        for table_from in communication.keys():
            connection = ''
            for table_to in communication[table_from]:
                table_to = table_to.items()
                first_item = list(table_to)[0]
                name_of_finish_table = first_item[0]
                key_from_start_table = (first_item[1])[0]
                key_from_finish_table = (first_item[1])[1]
                relation = f'{table_from}::{key_from_start_table} -- {name_of_finish_table}::{key_from_finish_table}\n'
                connection += relation
            communication_code += connection
        uml_code = '@startuml\n' \
                   'left to right direction' \
                   + f'\n{tables_code}\n' \
                   + f'{communication_code}\n' \
                   + '@enduml'
        print(tables_code)
        print(communication_code)
        print(uml_code)
        return uml_code

    def save_uml_code(self, uml_code: str, scale: int) -> None:
        """
        Func save uml-code in txt format.
        scale: image quality index. Optimal: 2.
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




