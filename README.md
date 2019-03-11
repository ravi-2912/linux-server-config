# Linux Server Configuration

This repository explains how to secure and set up a Linux distribution on a virtual machine, install and configure a database and web server, and finally to host a web application. The following are salient features of this project:

* Set up private virtual server using [Amazon AWS Ligthsail](https://aws.amazon.com/)
* Configure [Ubuntu 18.x](https://www.ubuntu.com/) as server
* User administration in [Ubuntu 18.x]
* Database administration using [PostgreSQL](https://www.postgresql.org/)
* Configure [Apache 2](https://httpd.apache.org/) server to host web application
* Host [Flask](http://flask.pocoo.org/) web application

## How to run

The application can be accessed by [http://35.177.147.191/](http://35.177.147.191/).

**Please note the above site is time limited and will be removed soon.**

Login to remote server

* As user `ubuntu`

    ```bash
    λ ssh -i yourKey.pem -p 2200 ubuntu@35.177.147.191
    ```

* As user `grader` 

    ```bash
    λ ssh -i grader.pem -p 2200 grader@35.177.147.191
    ```

## Configuration Steps

Detailed steps to configure, secure and host the web application in Ubuntu are described below stepwise.

### **Step 1** - Amazon AWS Lightsail

* Login to [Lightail](https://lightsail.aws.amazon.com)
* Go to *Account > Account* in the top nav bar
* Click *SSH Keys* in main body and create a new SSH key
* *Download* and save it on the PC
* Click *Home* in top nav bar and click *Create Instance*
* Select *OS Only > Ubuntu 18.04 LTS*
* In *SSH key pair manager* select the newly create key
* In *Identify your instance* give name to the server instance
* Finally click *Create Instance* at the end of main body and wait for it to start

For setting up firewall ports

* Click the 3 dots at top right of the newly created instance card and click *Manage*
* Note down the *Public IP* address - this will be used for login using the SSH key
* Click *Networking* and under *Firewall* clock *Add Another* to add the following two custome ports
  * *Application* - **Custom** , *Protocal* - **TCP** and *Port range* - **2200**
  * *Application* - **Custom** , *Protocal* - **UDP** and *Port range* - **123**
* Click *Save*

### **Step 2** - Remote login form Windows host using SSH

On you Windows terminal (I use [`λcmder`](https://cmder.net/))

* Navigate to the folder containing your SSH key
* Check the owners of the SSH key

  ```cmd
  λ cmd /c icacls yourKey.pem
  ```

* Remove inheritance from the SSH key

  ```cmd
  λ cmd /c icacls yourKey.pem /c /t /inheritance:d
  ```

* Remove all owners of the SSH key except the logged in user in Window

  ```cmd
  λ cmd /c icacls ravi.pem  /c /t /remove Administrator BUILTIN\Administrators BUILTIN Everyone System Users
  ```

* Login to Amazon AWS Lightsail Remote Server using SSH port 22 (default for Amazon AWS Lightsail)

  ```cmd
  λ ssh -i yourKey.pem -p 22 ubuntu@35.177.147.19
  ```

**Note** - The flag `-p 22` is for connecting to AWS via default SSH port. This port will be changed to 2200 for all SSH requests as explained later.

### **Step 3** - Configuring Ubuntu and system administration

After remote logging to system from Step 2 above the `λcmder` terminal will change as follows

```bash
ubuntu@ip-172-26-9-187:~$
```

The above will be referred as `u$>` in `bash ` code blocks presented below. If logged in as user `grader` the terminal will be referred as `g$>` in `bash` code blocks presented below.

#### Step 3.1 - Updates to Ubuntu

While logged in as `ubuntu@35.177.147.19` execute the commands below

* Update and upgrade

  ```bash
  u$> sudo apt-get update
  u$> sudo apt-get upgrade
  u$> sudo apt-get dist-upgrade
  ```

  Optional flag `-y` could be added at the end of each line to respond Yes to questions asked.

* Shutdown and restart

  ```bash
  u$> sudo shutdown -r now
  ```

* Configure local time to UTC and select your city

  ```bash
  u$> sudo dpkg-reconfigure tzdata
  ```

* Install ntp daemon ntpd for a better synchronization of the server's time over the network connection

  ```bash
  u$> sudo apt-get install ntp -y
  ```

* Enable automatic updates ([ref](https://libre-software.net/ubuntu-automatic-updates/))

  * Install unattended upgrades

    ```bash
    u$> sudo apt install unattended-upgrades -y
    ```

  * Edit `50unattended-upgrades` configuration file

    ```bash
    u$> sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
    ```

    and remove the two slashes (//) in the beginning of the line

    ```text
    "${distro_id}:${distro_codename}-updates";
    ```

  * Edit `20auto-upgrades` configuration file

    ```bash
    u$> sudo nano /etc/apt/apt.conf.d/20auto-upgrades
    ```

    and updates as follows

    ```text
    APT::Periodic::Update-Package-Lists "1";
    APT::Periodic::Download-Upgradeable-Packages "1";
    APT::Periodic::AutocleanInterval "7";
    APT::Periodic::Unattended-Upgrade "1";
    ```

*  Alternative to above step (with less control) is to execute the line below

    ```bash
    u$> sudo dpkg-reconfigure --priority=low unattended-upgrades
    ```

* Check if upgrades work

    ```bash
    u$> sudo unattended-upgrades --dry-run --debug
    ```

    Another way is

    ```bash
    u$> cat /var/log/unattended-upgrades/unattended-upgrades.log
    ```

* Restart the server

  ```bash
  u$> sudo shutdown -r now
  ```

#### Step 3.2 - Firewall and security settings

* Check status
* Default setting
* Allow port 2200 and 123 as TCP and UDP respectively
* Allow `www`, `http`, `ntp` and `ssh`
* Deny default `ssh`
* Show added

  ```bash
  u$> sudo ufw status
  u$> sudo ufw default deny incoming
  u$> sudo ufw default allow outgoing
  u$> sudo ufw allow 2200/tcp
  u$> sudo ufw allow 123/udp
  u$> sudo ufw allow http
  u$> sudo ufw allow www
  u$> sudo ufw allow ntp
  u$> sudo ufw allow ssh
  u$> sudo ufw show added
  ```

* Edit SSH configuration file and update SSH port to 2200

  ```bash
  u$> sudo ufw deny ssh
  u$> sudo nano /etc/ssh/sshd_config
  ```

* Enable, restart and check UFW status

  ```bash
  u$> sudo ufw enable
  u$> sudo service ssh restart
  u$> sudo ufw statu
  ```

* Logout from the remote server and login using port 2200

    ```bash
    u$> ssh -i yourKey.pem -p 2200 ubuntu@35.177.147.19
    ```

[`sendmail`](https://packages.ubuntu.com/bionic/sendmail) and [`fail2ban`](http://www.fail2ban.org/wiki/index.php/Main_Page) setup ([ref](https://www.digitalocean.com/community/tutorials/how-fail2ban-works-to-protect-services-on-a-linux-server
))

* Install dependencies and create a copy of `jain.conf` as `jail.local`

    ```bash
    u$> sudo apt-get install fail2ban sendmail iptables-persistent -y
    u$> sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
    ```

* Edit `jail.local` file and update as follows

    ```text
    destemail = yourEmail@hotmailgmail.com
    action = %(action_mwl)s
    ```

    Under `[sshd]` in `jail.local` file update the port to 2200

    ```text
    port = 2200
    ```

* Restart `fail2ban`

    ```bash
    u$> sudo service fail2ban restart
    ```

#### Step 3.3 - User administration

* Get exitig user list from either `λ less /etc/passwd` or `λ getent` or `λ getent passwd`
* Add user `grader` with password `grader` and full name `Udacity Grader`

    ```bash
    u$> sudo adduser grader
    ```

* Adduser `grader` to **sudoers** list

    ```bash
    u$> sudo visudo
    ```

    Add the following line under `root ALL=(ALL:ALL) ALL`

    ```text
    grader ALL=(ALL:ALL) ALL
    ```

    Allternatively add the above line to a new file `grader` as below

    ```bash
    u$> sudo nano /etc/sudoers.d/grader
    ```

* Check for sudo permissions

    ```bash
    u$> su - grader
    g$> sudo -l
    ```

* Create `.ssh` folder and create SSH pivate and public keys with name **authorized_keys**

    ```bash
    g$> mkdir .ssh
    g$> cd .ssh/
    g$> ssh-keygen
    ```

    Rename the keys

    ```bash
    g$> mv authorized_keys authorized_keys.rsa
    g$> mv authorized_keys.pub authorized_keys
    ```

    Change access permission, exit to user `ubuntu` and change ownership of `.ssh` folder

    ```bash
    g$> sudo chmod 700 /home/grader/.ssh/
    g$> sudo chmod 644 /home/grader/.ssh/authorized_keys
    g$> exit
    u$> sudo chown -R grader:grader /home/grader/
    u$> sudo chown -R grader:grader /home/grader/.ssh/
    ```

* Send the user `grader` private RSA key via email

    ```bash
    u$> su - grader
    g$> echo "Subject: Udacity Grader Key" | cat authorized_keys.rsa | /usr/sbin/sendmail -m "RSA  key for grader" -a authorized_keys.rsa -t yourEmail@hotmailgmail.com
    ```

    From email copy the text message and save it, using a notepad of choice, to `grader.pem` on the Windows host next to `yourKey.pem`.

### Step 4 - Setup PostgreSQL

* Instal dependencies

    ```bash
    λ sudo apt-get install postgresql postgresql-contrib -y
    ```

* Change to user `postgres` and run `psql` command

    ```bash
    λ sudo su - postgres
    λ psql
    ```

* Create PostgreSQL role `sportsitems` that can create database and check roles

    ```sql
    CREATE ROLE sportsitems WITH LOGN PASSWORD 'sportsitems';
    ALTER ROLE sportsitems CTREATEDB;
    \du
    \q
    ```

    Exit user `psotgres`

    ```bash
    λ exit
    ```

* Create user `sportsitems` with passoword `sportsitems` and add to **sudoers** list


    ```bash
    λ sudo adduser sportsitems
    λ sudo visudo
    ```

    Add the line below `grader`

    ```text
    sportsitems ALL=(ALL:ALL) ALL
    ```

* Change user to `sportsitems` and creasate database named `sportsitems`


    ```bash
    λ su - sportsitems
    λ sudo -l
    λ createdb sportsitems
    λ psql
    ```

    Verify is `sportsitems` databse exists and exit

    ```sql
    \l
    \q
    ```

    Change baxk to user `ubuntu`

    ```bash
    λ exit
    ```

### Step 5 - Setup Apache2, Python and Git

* Install dependencies

    ```bash
    λ sudo apt-get install python3 python3-pip apache2 libapache2-mod-wsgi-py3 git git-sh libpq-dev
    ```

    `git-sh` provides git bash for managing git repositories

* Start Apache2 service and enable WSGI mod

    ```bash
    λ sudo service apache2 start
    λ sudo service apache2 status
    λ sudo a2enmod wsgi
    ```

* Install python module `virtualenv` as user `grader`

    ```bash
    λ su - grader
    λ sudo pip3 install virtualenv
    ```

* Configure git

    ```bash
    λ git config --global user.name "yourUserName"
    λ git config --global user.email "yourEmail@hotmailgmail.com"
    ```

### Step 6 - Website setup and Apache 2 configuration

A [Flask](http://flask.pocoo.org/) website is provided in this repository in folder `flaskitemscatalog`. The website project structure is described below

```tree
flaskitemscatalog
│   fill_db.py
│   README.md
│   run.wsgi
│
└───flaskitemscatalog
    │   client_secret.json
    │   routes.py
    │   sportsitems_db.py
    │   __init__.py
    │
    ├───static
    │       styles.css
    │
    └───templates
            cat_op.html
            home.html
            index.html
            item_op.html
            item_view.html
            login.html
```

The `run.wsgi` is modified to include Apache2 logging and to use the virtual environment that will be created. The `__init__.py` is modified to include all routes and to run the Flask app.

#### Step 6.1 - Website setup

* As user `grader` clone the repository, then move it to parent folder and change its ownership

    ``` bash
    λ su - grader
    λ cd /var/www
    λ sudo git clone https://github.com/ravi-2912/linux-server-config.git
    λ cd linux-server-config
    λ sudo mv flaskitemscatalog .
    ```

* Create python virtual environment and install dependencies as user `grader`

    ```bash
    λ cd /var/www/flaskitemscatalog/flaskitemscatalog
    λ sudo virtualenv -p python3 venv3
    λ . venv3/bin/activate
    (venv3) λ pip3 install flask httplib2 requests sqlalchemy bleach psycopg2 psycopg2-binary
    (venv3) λ pip3 install --upgrade oauth2client
    ```

* Run python files to create database `sportsitems` and fill it and then deactivate the environment

    ```bash
    (venv3) λ python3 sportsitems_dp.py
    (venv3) λ cd /var/www/flaskitemscatalog
    (venv3) λ python3 fill_db.py
    (venv3) λ deactivate
    ```

    Note, before issuing `deactivate` command test that `__init__.py` runs.

    ```bash
    (venv3) λ cd /var/www/flaskitemscatalog/flaskitemscatalog
    (venv3) λ python3 __init__.py
    ```

    The above should serve the webiste to `localhost` at port 5000.

* Change ownership of folder `flaskitemscatalog` to user `grader`

    ```bash
    λ cd /var/www
    λ sudo chown -R grader:grader flaskitemscatalog/
    ```

#### Step 6.2 - Apache 2 configuration

* Provide WSGI Python PAth in the `wsgi.conf` file

    ```bash
    λ sudo nano /etc/apache2/mods-enabled/wsgi.conf
    ```

    Add the following line underneatht the line starting with `#WSGIPythonPath...`

    ```text
    WSGIPythonPath /var/www/flaskitemscatalog/flaskitemscatalog/venv3/lib/python3.6/site-packages
    ```

    Note in above a check must be made to ensure Python version 3.6 or higher is available.

* Create and fille the Apache2 sites-available `conf` file for `flaskitemscatalog` website

    ```bash
    λ sudo nano /etc/apache2/sites-available/flaskitemscatalog.conf
    ```

    Insert the content below into `flaskitemscatalog.conf` file

    ```xml
    <VirtualHost *:80>
                ServerName 35.177.147.191
                ServerAdmin grader@35.177.147.191

                WSGIScriptAlias / /var/www/flaskitemscatalog/run.wsgi
                <Directory /var/www/flaskitemscatalog/flaskitemscatalog/>
                        Order allow,deny
                        Allow from all
                </Directory>

                Alias /static /var/www/flaskitemscatalog/flaskitemscatalog/static
                <Directory /var/www/flaskitemscatalog/flasitemscatalog/static/>
                        Order allow,deny
                        Allow from all
                </Directory>

                ErrorLog ${APACHE_LOG_DIR}/error.log
                LogLevel warn
                CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>
    ```

* Enable site, disable defautl site and restart Apache2 server

    ```bash
    λ sudo a2ensite flaskitemscatalog
    λ sudo a2dissite 000-default.conf
    λ sudo systemctl reload apache2
    λ sudo service apache2 restart
    λ sudo service apache2 status
    ```

* Check Apache 2 configuration file

    ```bash
    λ apachectl configtest
    ```

* Access in Windows host by clicking this link [http://35.177.147.191/](http://35.177.147.191/)
* Debugging Apache 2 server

    ```bash
    λ cat /var/log/apache2/error.log
    ```

    This is important step in case the website is not working. Reviewing the last few lines of `error.log` to understand. This will commonly require to modify import parths in python files or check database (which can be done using `psql`) or modifying paths in Apache 2 configuration files for the webite or DBURI string for SQLAlchemy.

* Exit the user `grader` and then `ubuntu`

    ```bash
    λ exit
    λ exit
    ```

### Step 7 - Udacity Grader access

* Udacity's Grader to access the remote server using the command below and the SSH key `grader.pem` provided in the repository

    ```bash
    λ ssh -i grader.pem -p 2200 grader@35.177.147.191
    ```