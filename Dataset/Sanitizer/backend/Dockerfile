
FROM python:3



COPY . /Dataset/Sanitizer
WORKDIR /Dataset/Sanitizer/backend

CMD sleep 3000
lRUN pip install --no-cache-dir -r ./requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/Dataset"

CMD python ./backend.py
