FROM python:3.9.7-alpine
WORKDIR /app
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 5002
CMD ["python", "main.py"]