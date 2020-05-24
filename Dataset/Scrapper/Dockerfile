
FROM jjanzic/docker-python3-opencv


#RUN mkdir -p /Scrapper

COPY . /Dataset
WORKDIR /Dataset


RUN apt-get update
RUN apt-get install tree

RUN pip install --no-cache-dir -r ./Scrapper/requirements.txt

#CMD tree
#CMD sleep 300
#CMD tree
CMD python ./Scrapper/main.py
