FROM python:3

COPY src/main.py ./

RUN pip3 install flask requests python-dateutil

CMD ["python3", "main.py"]
