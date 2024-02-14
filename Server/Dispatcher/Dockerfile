FROM python:3.9.6

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]