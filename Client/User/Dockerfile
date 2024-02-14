FROM python:3.9.6

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . app/

EXPOSE 8500

WORKDIR /app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port", "8500"]