FROM python:3


COPY . /Dataset
WORKDIR /Dataset/Scrapper

#CMD sleep 3000
RUN pip install --no-cache-dir -r ./requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/Dataset"

CMD python ./main.py --double_check True --meta True --images True
