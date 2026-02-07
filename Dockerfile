# Dockerfile - Otimizado para produção
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements primeiro (cache de layer)
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia todo o código
COPY . /app/

# Cria diretórios necessários
RUN mkdir -p /app/logs /app/media /app/staticfiles

# Permissões adequadas
RUN chmod -R 755 /app

EXPOSE 8000

# Usa Gunicorn em produção
CMD ["gunicorn", "plataforma.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]