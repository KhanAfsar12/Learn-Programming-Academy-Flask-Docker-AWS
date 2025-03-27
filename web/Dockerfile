FROM python:3.10
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary=:all: spacy
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]