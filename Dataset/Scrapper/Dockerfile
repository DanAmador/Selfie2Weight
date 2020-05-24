
FROM jjanzic/docker-python3-opencv



COPY . /Dataset
WORKDIR /Dataset/Scrapper

#CMD sleep 3000
RUN pip install --no-cache-dir -r ./requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/Dataset"

CMD python ./main.py
