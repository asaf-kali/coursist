# Coursist
Course + Assist, get it?

## Description
This project is intended for university students all around the world.<br>
The main features that this project supplies are:
1. Social course review system.
1. Semestrial courses schedule building tool.
1. Course program planning for the entire degree.

## Installation
*Important: You will need `python 3.7+` to run this project.*
1. Clone the project.
1. Create a [virtual environment](https://docs.python.org/3/tutorial/venv.html)
(if you use `Pycharm`, [you can do it like that](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html)). 
1. In the terminal, make sure that when you type `python` you use the virtual environment's python<br>
(If you use `Pycharm` that will happen by default in the integrated terminal, otherwise you will need to
use the [source](https://docs.python.org/3/tutorial/venv.html) command).
1. Run `make install` (if you dont have `make` installed, just run the commands under `install` inside the `Makefile`).

## Usage
#### Basics
First, you need to run the local server:
1. Run `python manage.py runserver`.
1. Open [http://localhost:8000](http://localhost:8000) in your preferred web browser.

If everything went well, the server is now running on your local machine. Let's create an admin user:
1. Run `python manage.py createsuperuser` and follow the creation process.
1. Open [http://localhost:8000/admin](http://localhost:8000/admin) and log in with your new admin user.

Now you can see and control the entire database and the system's objects.

#### Management commands
The server allows to run these custom commands:
1. `python manage.py dev_init`: Initiates the database with dummy data for development purposes.
1. `python manage.py retreive_courses`: Retrieves courses data from specified servers (*TO BE IMPLEMENTED*). 

## Contribution
Before committing any change, please run `make black` in the terminal. 

## Related Docs
1. Styles template: https://bootswatch.com/litera/
1. Rating system: https://github.com/wildfish/django-star-ratings
1. DB backup: https://django-dbbackup.readthedocs.io/en/stable/index.html
1. Cron jobs: https://django-cron.readthedocs.io/en/latest/index.html

## Disclaimer
This project is part of the Open Source Workshop (67118) course team project.
