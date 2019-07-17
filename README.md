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
- Okapi
  - Java 1.8
- supervisor
  - Optional

## Installation
### Okapi
Set the PATH
### Django migrate
```
python manage.py migrate
python manage.py createsuperuser
chmod 766 db.sqlite3
mkdir media
```
### supervisor
#### install
```
yum install supervisor
sudo vi /etc/supervisord.d/process_tasks.ini
```
#### config
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
#### start
```
sudo service supervisord start
```
#### autostart
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
### change model
```
python manage.py makemigrations
python manage.py migrate
```
