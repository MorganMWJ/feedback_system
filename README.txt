The highest level directory contains my project diary and a text file listing commands
I found useful during development, what they do and how to use them.

The Deliverables directory contains items of work that were produced throughout
the project and then brought together in the final report, this directory also contain the final report.

The technical_work directory contains my code in the project_code directory and the requirements.txt file
which can be used to install python packages my project depends on using the ‘pip install -r requirements.txt’ command. 


The application requires access to a PostgreSQL database to run. 
I had to create a postgreSQL database cluster to set it up: https://www.postgresql.org/docs/9.3/runtime.html
Django requires the info for the server to be provided by setting the DATABASES variable in
the project_code/feedback_system/settings.py file.

This is what mine looked like during development:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'majorprojectdb',
        'USER': 'postgres',
        'PASSWORD': 'major_project',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

The database will have to created from SQL migrations.
python manage.py makemigrations
python manage.py migrate
Will do this.

python manage.py runserver 0.0.0.0:8000
Will then run the server on all available hosts defiend in the settings.py ALLOWED_HOSTS variable.