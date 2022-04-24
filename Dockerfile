FROM python:3.8.13-bullseye

RUN pip install git+https://github.com/tdh8316/triangler.git@v0.4 --upgrade
RUN pip install git+https://github.com/sedthh/pyxelate.git --upgrade

WORKDIR /opt/backend
COPY . .
RUN pip install -r requirements.txt

RUN python manage.py makemigrations
RUN python manage.py migrate

ENTRYPOINT python manage.py runserver 0.0.0.0:8000
