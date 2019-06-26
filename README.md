# kon-nyaku
File translator used Google Translator API

## Requiments
- Python 3.x
    - `pip install Django`
    - `pip install bootstrap4`
    - `pip install django-background-tasks`
    - `pip install google-cloud-translate`
    - `pip install django-bootstrap4`
- Okapi
  - Java 1.8

## Installation
### Okapi
Set the PATH
### Django migrate
```
python manage.py migrate
python manage.py createsuperuser
```
### Set Google credential
See this [site](https://cloud.google.com/translate/docs/quickstart-client-libraries).

## Usage
```
#run background tasks
python manage.py process_tasks

#run server
python manage.py runserver
```
