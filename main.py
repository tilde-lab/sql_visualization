"""
Program launch.
"""
from diagram_builder import DiagramBuilder
from postgre_handler import PostgreSQL_handler

try:
    tables_structure, foreign_keys_for_diagram_builder, keys_in_table, number_of_keys, primary_keys = \
        PostgreSQL_handler().start_handler()
except NameError:
    print('Attention! In db not tables.')
else:
    d_bild = DiagramBuilder()
    uml_code = d_bild.constructor(
        tables_structure, foreign_keys_for_diagram_builder, keys_in_table, number_of_keys, primary_keys
    )
    d_bild.save_uml_code(uml_code, 3)
    d_bild.build_diagram()