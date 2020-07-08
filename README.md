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


### Docker images
1. To build the docker image inside the project root directory:
```shell
docker build -t coursist:latest .
```

2. To run the server locally on port `8000`:
```shell
docker run -it -p 8000:8000 coursist:latest 0.0.0.0:8000
```
Login as usual to: http://localhost:8000/

## Usage
#### Basics
First, you need to run the local server:
1. Run `python manage.py runserver` (If you use `Pycharm` it should detect this is a Django project,
so you will be able to run the server without a terminal command).
1. Open [http://localhost:8000](http://localhost:8000) in your preferred web browser.

If everything went well, the server is now running on your local machine.
You can use the site as a regular user (Facebook and Google login won't work).<br>
The installation process also created an admin user: its user name is `admin` and the password is `123456`.
Open [http://localhost:8000/admin](http://localhost:8000/admin) and log in with your admin user.
Now you can see and control the entire database and the system's models.

#### Management commands
The server allows to run these custom commands:
1. `python manage.py dev_init`: Initiates the database with dummy data for development purposes.
1. `python manage.py fetch_courses`: Retrieves courses data from HUJI servers.<br>
Run `python manage.py help fetch_courses` to learn about the `limit` and `fetch_existing` arguments.

## Contribution
1. Inside github, fork the [upstream repository](https://github.com/asaf-kali/coursist).
1. Clone your own fork of the project.
1. Before starting to implement a new feature or a bug fix, make sure to pull `master` (or `develop`) branch
from the [upstream repository](https://github.com/asaf-kali/coursist), and only then create your branch.
1. While developing, please add and fix any relevant tests.
1. Before opening a PR, make sure to use both `python manage.py test` to test that everything still works,
and use `make black` to achieve well-formatted code.
1. Push your code and open a PR against the [upstream repository](https://github.com/asaf-kali/coursist)
`develop` branch. 

## Related Docs
1. Styles template: https://bootswatch.com/litera/
1. Rating system: https://github.com/wildfish/django-star-ratings
1. DB backup: https://django-dbbackup.readthedocs.io/en/stable/index.html
1. Cron jobs: https://django-cron.readthedocs.io/en/latest/index.html

## Disclaimer
This project is part of the Open Source Workshop (67118) course team project.
