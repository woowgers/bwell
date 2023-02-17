from app import create_app
import sys


project_home = ""  # path to applicaiton instance folder
if project_home not in sys.path:
    sys.path = [project_home] + sys.path


application = create_app()
