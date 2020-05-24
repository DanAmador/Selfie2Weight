
FROM jjanzic/docker-python3-opencv



COPY . /Dataset
WORKDIR /Dataset

#CMD sleep 3000
RUN pip install --no-cache-dir -r ./Scrapper/requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/Dataset"

CMD python ./Scrapper/main.py
