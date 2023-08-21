# database_visualization
Generate Entity-Relationship Diagrams from PostgreSQL by PlantUML, DBML-renderer, ERAlchemy, Graphviz.
### Requirements
- PostgreSQL*
- graphviz==2.49.0
- dbml-renderer==1.0.27
- plantuml (specific version present in the repository)
- npm==9.6.7
- node==v18.17.0
- Java Runtime Environment* 
## Installation
To download repository:
```bash
git clone https://github.com/alinzh/database_visualization.git
```

Install Graphviz for your version of Windows by following this link:
https://graphviz.org/download/ 

Install Graphviz on Linux:

```bash
sudo apt-get install graphviz libgraphviz-dev
```

Next:

```bash
pip install -r requirements.txt
sudo npm install -g @softwaretechnik/dbml-renderer
```
Run:

```bash
python main.py --host HOST --port PORT --user USER --password PASSWORD \
--db_name DB_NAME --schema_name SCHEMA_NAME --engine ENGINE --direction DIRECTION --output_path PATH
```
*DIRECTION*, *ENGINE* and *PATH* are optional arguments.

**Available engines:**

- 'plantuml'
- 'eralchemy'
- 'dbml-r'
- 'dot-r'

**Available direction:**

If you are not satisfied with the location of the blocks on the diagram, change their location by adding the argument *DIRECTION* = '2'.

If you need to save image in specific folder, add an argument *PATH* with a path before it.








