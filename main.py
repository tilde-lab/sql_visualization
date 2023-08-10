"""
Program launch.

The program uses from the console. To run it, you need to go to the project directory,
use the command in the console:

$ python main.py --host HOST --port PORT --user USER --password PASSWORD --db_name DB_NAME --schema_name SCHEMA_NAME --engine ENGINE
"""
import argparse
from diagram_builder import PlantUMLBilder
from postgre_handler import PostgreSQL_handler
from dbml_renderer_handler import DBMLRenderer


def main(host, port, user, password, db_name, schema_name, engine=None):
    try:
        answer = \
            PostgreSQL_handler(host, port, user, password, db_name, schema_name).start_handler()
    except NameError:
        print('Attention! In db not tables.')
    else:
        if answer:
            tables_structure, foreign_keys_for_diagram_builder, keys_in_table, \
                number_of_keys, primary_keys, column_types = answer
            if engine == 'plantuml':
                PlantUMLBilder(db_name).start_handler(
                    tables_structure, foreign_keys_for_diagram_builder, keys_in_table, primary_keys
                )
            if engine == 'dbml-r':
                DBMLRenderer(db_name).start_handler(
                    tables_structure, foreign_keys_for_diagram_builder, primary_keys, column_types
                )
            # Will doing diagrams by 2 way if type of engine does not choose.
            else:
                DBMLRenderer(db_name).start_handler(
                     tables_structure, foreign_keys_for_diagram_builder, primary_keys, column_types
                )
                PlantUMLBilder(db_name).start_handler(
                    tables_structure, foreign_keys_for_diagram_builder, keys_in_table, primary_keys
                )

# Launching the program from console.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diagram Builder")
    parser.add_argument("--host", required=True, help="Database host")
    parser.add_argument("--port", required=True, help="Database port")
    parser.add_argument("--user", required=True, help="Database user")
    parser.add_argument("--password", required=True, help="Database password")
    parser.add_argument("--db_name", required=True, help="Database name")
    parser.add_argument("--schema_name", required=True, help="Schema name")
    parser.add_argument(
        "--engine", required=True, help="Select how the diagram is rendered. Available 2 type.\n"
                         "PlantUML - write 'plantuml'.\nDBML-renderer - write 'dbml-r'.")

    args = parser.parse_args()
    main(args.host, args.port, args.user, args.password, args.db_name, args.schema_name, args.engine)


