FROM python:3.10

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y tesseract-ocr

RUN pip install -r requirements.txt

CMD ["gunicorn", "app:app"]