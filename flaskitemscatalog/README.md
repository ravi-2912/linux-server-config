# Sports Item - Flask App

Flask python app to for catalogin sports items. The app features database create, read, and update (CRUD) operations,registered user login, login from third party ([Gmail](https://www.google.com/gmail/
)) and html templating. The app salient feautures are

* Database CRUD operations
* User database and login
* Gmail login
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

### TODO

* Add [bcrypt](https://github.com/pyca/bcrypt/) passowrd hashing
* Add user registration and email verification
* Manage duplicate entries (this is an exsiting bug)