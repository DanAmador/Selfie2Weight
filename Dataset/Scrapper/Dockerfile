FROM python:3.7






RUN mkdir -p /Scrapper
WORKDIR /Scrapper

COPY requirements.txt /Scrapper/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY .. /.


CMD python main.py
