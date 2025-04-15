FROM python:3.10-slim

# Gerekli paketler
RUN apt-get update && apt-get install -y default-mysql-client && apt-get clean

# Uygulama dosyalarını kopyala
WORKDIR /app
COPY . /app

# Bağımlılıkları yükle
RUN pip install -r requirements.txt

CMD ["python", "data.py"]
