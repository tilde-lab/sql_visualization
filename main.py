"""
Program launch.
"""
from diagram_builder import DiagramBuilder
import data_for_tests
from postgre_handler import PostgreSQL_handler

tables_structure, foreign_keys_for_diagram_builder = PostgreSQL_handler().start_handler()
d_bild = DiagramBuilder(data_for_tests.db_name)
uml_code = d_bild.constructor(tables_structure, foreign_keys_for_diagram_builder)
d_bild.save_uml_code(uml_code, 3)
d_bild.build_diagram()