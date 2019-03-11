# Sports Item - Flask App

**Original repository link:** [https://github.com/ravi-2912/flask-items-catalog](https://github.com/ravi-2912/flask-items-catalog)

This app is modified to run under [Ubuntu 18](https://www.ubuntu.com/) with [Apache 2 server](https://httpd.apache.org/) served by [Amazon AWS Lightsail](https://aws.amazon.com/).

Flask python app to for catalogin sports items. The app features database create, read, and update (CRUD) operations, registered user login and html templating. The app salient feautures are

* Database CRUD operations
* User database and login
* HTML Templating
* JSON endpoint (REST API)

## How to run
Run the app as follows:

```bash
$> python app.py
```

And then open [localhost:8000](http://localhost:8000/).

There is user registration at this point hence you can use either your gmail account or use the dummy user login. Dummy user login are provided in the `fill_db.py`. You can login using _jdoe_ with password _jdoe_2007_.

## Python Dependencies

The app was developed using [Anaconda Python](https://www.anaconda.com/) environment which has most of the tools already used. There may be requirement for you to install google api library `oauth2client` and `httplib2` which can be done as below:

```bash
$> pip install oauth2client
$> pip install httplib2
```

## Modifications to serve usign Apache2

* Modfication to `run.wsgi`

```python
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
```

* Modififcation to `__init__.py` basically includes all routes from `routes.py` and at the end of file `__init__.py` the following code is included

```python
if __name__ == "__main__":
    app.run()
```

* The `__init__.py` file is also modified to comment the code to import `fill_dp.py` and calls to database function `DB_Main()` and `fillDB()`.

