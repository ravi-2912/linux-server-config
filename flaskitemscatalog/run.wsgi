activate_this = '/var/www/flaskitemscatalog/flaskitemscatalog/venv3/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/flaskitemscatalog/")

from flaskitemscatalog import app as application

application.secret_key = "super secret key"
