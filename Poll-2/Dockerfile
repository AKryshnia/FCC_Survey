FROM python:3.11-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Устанавливаем обновления и необходимые модули
RUN apk update && apk add --no-cache \
    libpq \
    gcc \
    g++ \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    openssl-dev \
    zlib-dev \
    jpeg-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    harfbuzz-dev \
    fribidi-dev \
    cairo-dev \
    pango-dev \
    gdk-pixbuf-dev \
    librsvg-dev \
    ttf-freefont

# Обновление pip python
RUN pip install --upgrade pip

# Установка пакетов для проекта
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app

# Копирование проекта
COPY . .

# Настройка записи и доступа
RUN chmod -R 777 ./