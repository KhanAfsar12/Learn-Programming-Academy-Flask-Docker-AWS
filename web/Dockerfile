FROM python:3.10
WORKDIR /usr/src/app
RUN python -m pip install --no-cache-dir spacy
RUN python -m spacy download en_core_web_sm
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]