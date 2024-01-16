import sys

from bwell.app import create_app

project_home = ""
if project_home not in sys.path:
    sys.path = [project_home, *sys.path]

application = create_app()
