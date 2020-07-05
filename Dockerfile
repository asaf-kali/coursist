FROM python:3.8
WORKDIR /code
COPY requirements.txt /code
COPY requirements-dev.txt /code
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

COPY . /code
ENV PYTHONPATH /code
RUN ["python", "manage.py", "migrate"]
ENTRYPOINT ["python", "manage.py", "runserver"]
