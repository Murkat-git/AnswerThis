FROM python:3.9.6

RUN apt-get update && apt-get install -y libmagic-dev poppler-utils libgl1 poppler-utils libreoffice pandoc tesseract-ocr libtesseract-dev tesseract-ocr-rus


COPY requirements.txt .
RUN pip install -r requirements.txt

RUN python -c "import nltk; nltk.download('punkt')" && \
    python -c "import nltk; nltk.download('averaged_perceptron_tagger')"

COPY . app/

EXPOSE 8501

WORKDIR /app
ENTRYPOINT ["streamlit", "run", "app.py"]