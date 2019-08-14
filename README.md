# kon-nyaku
File translator used Google Translator API

## Requiments
- Python 3.x
    - `pip install Django`
    - `pip install bootstrap4`
    - `pip install django-background-tasks`
    - `pip install google-cloud-translate`
    - `pip install django-bootstrap4`
    - `pip install lxml`
    - `pip install environ`
    - `pip install django-crontab`
    - `pip install python-dateutil`
- Okapi
  - Java 1.8
- supervisor
  - Optional

## Installation
### Okapi
Set the PATH
### Django migrate
```
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py collectstatic
python3 manage.py crontab add
chmod 766 db.sqlite3
mkdir media
mkdir log
```

### supervisor
#### Install
```
yum install supervisor
sudo vi /etc/supervisord.d/process_tasks.ini
```
#### Config
```
[program:process_tasks]
command=python3 /home/<username>/kon_nyaku/manage.py process_tasks
user=<username>
autostart=true
autorestart=true
environment=PATH="<okapi path>:/usr/bin:$(ENV_PATH)s"
stdout_logfile=/var/log/supervisor/jobs/process_tasks.log
stdout_logfile_maxbytes=1MB
stdout_logfile_backups=5
stdout_capture_maxbytes=1MB
redirect_stderr=true
```
#### Start
```
sudo service supervisord start
```
#### Autostart
```
sudo systemctl enable supervisord.service
```

### Set Google credential
See this [site](https://cloud.google.com/translate/docs/quickstart-client-libraries).

## Usage for Dev env
```
#run background tasks
python manage.py process_tasks

#run server
python manage.py runserver
```
## Tips for develop
### Change model
If model is changes, you should run the following command.
```
python manage.py makemigrations
python manage.py migrate
```

## Tips for production
### Change static files (js and css)
If static files are changes, you should run the following command.
```
python manage.py collectstatic
```
### Change model
If model is changes, you should run the following command.
```
python manage.py migrate
```
