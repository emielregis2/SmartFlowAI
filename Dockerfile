# SmartFlowAI - Dockerfile dla produkcji
FROM python:3.11-slim

# Metadane
LABEL maintainer="SmartFlowAI Team"
LABEL version="1.0.0"
LABEL description="SmartFlowAI - Aplikacja do analizy procesów biznesowych"

# Zmienne środowiskowe
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Tworzenie użytkownika bez uprawnień root
RUN groupadd -r smartflow && useradd -r -g smartflow smartflow

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie plików wymagań
COPY requirements.txt .

# Instalacja zależności Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu aplikacji
COPY . .

# Tworzenie katalogów dla logów i danych
RUN mkdir -p /app/logs /app/data && \
    chown -R smartflow:smartflow /app

# Przełączenie na użytkownika bez uprawnień root
USER smartflow

# Sprawdzenie zdrowia aplikacji
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Eksponowanie portu
EXPOSE 8501

# Komenda startowa
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"] 