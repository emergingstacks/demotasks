FROM python:alpine
WORKDIR /opt
COPY . .
RUN pip3 install -r requirements.txt
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENTRYPOINT ["python3", "loki.py"]