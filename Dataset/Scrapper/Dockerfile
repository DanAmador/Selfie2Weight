FROM python:3.7

COPY poetry.lock /
COPY pyproject.toml .
RUN pip install poetry && \
    poetry config settings.virtualenvs.create false && \
    poetry install

COPY . /
CMD python main.py