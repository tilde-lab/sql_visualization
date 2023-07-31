"""
Program launch.
"""
from diagram_builder import DiagramBuilder
import data_for_tests

d_bild = DiagramBuilder(data_for_tests.db_name)
uml_code = d_bild.constructor(data_for_tests.tables, data_for_tests.communication)
d_bild.save_uml_code(uml_code, 3)
d_bild.build_diagram()