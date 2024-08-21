FROM python:3.11-alpine
RUN apk update
RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
COPY ./app ./app
COPY ./.env ./app/.env
COPY ./data ./data
CMD ["streamlit", "run", "app/app.py"]