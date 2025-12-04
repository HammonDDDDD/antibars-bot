# 🚀 Деплой Telegram Бота на Удалённый Сервер с Docker Compose

## 📋 Предварительные требования

На сервере должны быть установлены:
- **Docker** (версия 20.10+)
- **Docker Compose** (версия 2.0+)
- **Git** (для клонирования репо)

### Установка Docker и Docker Compose на Linux

```bash
# Обновляем пакеты
sudo apt-get update && sudo apt-get upgrade -y

# Устанавливаем Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавляем текущего пользователя в группу docker (чтобы не писать sudo)
sudo usermod -aG docker $USER
newgrp docker

# Устанавливаем Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Проверяем установку
docker --version
docker-compose --version
```

---

## 📂 Подготовка проекта

### 1️⃣ Клонируем репозиторий на сервер

```bash
# Переходим в нужную директорию (например, /opt)
cd /opt

# Клонируем репозиторий
git clone https://github.com/твой-пользователь/HammonDDDDD.git antibars-bot
cd antibars-bot/lab4

# Или скопируем файлы через SCP
# scp -r ./lab4/* user@server.com:/opt/antibars-bot/
```

### 2️⃣ Копируем Google Sheets credentials

**ВАЖНО:** Файл `antibars-credentials.json` содержит секретные данные!

```bash
# На локальной машине отправляем на сервер:
scp antibars-credentials.json user@server.com:/opt/antibars-bot/

# На сервере проверяем, что файл на месте:
ls -la antibars-credentials.json
```

### 3️⃣ Создаём директории для данных

```bash
# На сервере в директории /opt/antibars-bot/
mkdir -p data logs

# Копируем credentials в data/ (если еще не там)
cp antibars-credentials.json data/

# Устанавливаем права доступа
chmod 600 data/antibars-credentials.json
```

### 4️⃣ Создаём .env файл

```bash
# На сервере в /opt/antibars-bot/
cp .env.example .env

# Редактируем (замени токен на свой)
nano .env
```

Содержимое `.env`:
```
BOT_TOKEN=твой_токен_здесь
PYTHONUNBUFFERED=1
```

---

## 🐳 Запуск Docker Compose

### 1️⃣ Сборка образа

```bash
# Находимся в /opt/antibars-bot/
docker-compose build --no-cache
```

### 2️⃣ Запуск контейнера

```bash
# Запуск в фоновом режиме (-d = detach)
docker-compose up -d

# Или для тестирования (видим логи в реальном времени)
docker-compose up

# Нажми Ctrl+C если запускал в интерактивном режиме
```

### 3️⃣ Проверка статуса

```bash
# Смотрим, запущен ли контейнер
docker-compose ps

# Смотрим логи
docker-compose logs -f antibars-bot

# Последние 100 строк логов
docker-compose logs --tail=100 antibars-bot

# Остановить контейнер
docker-compose down

# Перезапустить
docker-compose restart
```

---

## 📊 Мониторинг и Управление

### Просмотр логов в реальном времени

```bash
docker-compose logs -f antibars-bot

# Выход из логов: Ctrl+C
```

### Проверка ресурсов

```bash
# Сколько памяти/CPU используется контейнер
docker stats antibars-bot
```

### Вход в контейнер (для отладки)

```bash
docker-compose exec antibars-bot bash

# Или если нужен Python shell
docker-compose exec antibars-bot python3

# Выход: exit
```

### Проверка БД внутри контейнера

```bash
docker-compose exec antibars-bot sqlite3 data/bars_db.sqlite ".tables"
```

---

## 🔧 Обновление кода

Если обновил код на GitHub:

```bash
# Переходим в директорию проекта
cd /opt/antibars-bot

# Обновляем код
git pull

# Пересобираем образ
docker-compose build

# Перезапускаем контейнер
docker-compose up -d

# Проверяем логи
docker-compose logs -f antibars-bot
```

---

## 🆘 Решение проблем

### Контейнер падает сразу после запуска

```bash
# Проверяем логи
docker-compose logs antibars-bot

# Возможные ошибки:
# 1. Нет файла antibars-credentials.json
# 2. Неправильный BOT_TOKEN в .env
# 3. Нет интернета на сервере
```

### Ошибка при подключении к Google Sheets

```bash
# Проверяем, что credentials файл на месте
ls -la data/antibars-credentials.json

# Проверяем права
chmod 600 data/antibars-credentials.json

# Перезапускаем контейнер
docker-compose restart antibars-bot
```

### Контейнер использует слишком много памяти

```bash
# Проверяем текущее использование
docker stats antibars-bot

# Уменьшаем лимиты в docker-compose.yml (если нужно)
# Перезапускаем после изменения
docker-compose up -d
```

### Нужно очистить все данные и начать заново

```bash
# Остановляем контейнер
docker-compose down

# Удаляем image
docker rmi antibars-bot:latest

# Удаляем БД (осторожно!)
rm data/bars_db.sqlite

# Пересобираем и запускаем
docker-compose build
docker-compose up -d
```

---

## 🔐 Безопасность

### 1️⃣ Защита .env файла

```bash
# На сервере ограничиваем доступ к .env
chmod 600 .env

# Или вообще не держим secrets в файле, используем docker secrets
```

### 2️⃣ Регулярное обновление

```bash
# Регулярно обновляй код и образы
git pull
docker-compose build
docker-compose up -d
```

### 3️⃣ Backup БД

```bash
# Создание backup
docker-compose exec antibars-bot cp data/bars_db.sqlite data/bars_db.sqlite.backup

# Или на локальной машине
scp user@server.com:/opt/antibars-bot/data/bars_db.sqlite ./backup/bars_db.sqlite.backup
```

---

## ✅ Проверка, что всё работает

1. **Бот запущен:**
   ```bash
   docker-compose ps
   # Должно показать контейнер в статусе "Up"
   ```

2. **Логи чистые:**
   ```bash
   docker-compose logs antibars-bot | tail -20
   # Не должно быть ошибок
   ```

3. **Тестируем команды бота в Telegram:**
   - `/weather Москва`
   - `/quote`
   - `/headlines`
   - `/set_isu 123456`

4. **Проверяем, что БД создалась:**
   ```bash
   docker-compose exec antibars-bot ls -la data/
   # Должны быть: bars_db.sqlite, antibars-credentials.json
   ```

---

## 📝 Дополнительно: Автозапуск при перезагрузке сервера

```bash
# Docker Compose уже имеет restart: unless-stopped
# Контейнер автоматически перезапустится при перезагрузке сервера

# Если хочешь добавить в systemd (опционально):
# Создай файл /etc/systemd/system/antibars-bot.service
```

**Содержимое `/etc/systemd/system/antibars-bot.service`:**
```ini
[Unit]
Description=AntiBars Telegram Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/antibars-bot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl enable antibars-bot.service
sudo systemctl start antibars-bot.service
sudo systemctl status antibars-bot.service
```

---

## 🎯 Итоговая чек-лист

- [ ] Docker и Docker Compose установлены на сервере
- [ ] Проект клонирован или загружен на сервер
- [ ] Файл `antibars-credentials.json` скопирован в директорию проекта
- [ ] Создан `.env` файл с корректным BOT_TOKEN
- [ ] Созданы директории `data/` и `logs/`
- [ ] Выполнена сборка: `docker-compose build`
- [ ] Запущен контейнер: `docker-compose up -d`
- [ ] Проверены логи: `docker-compose logs -f antibars-bot`
- [ ] Бот отвечает на команды в Telegram

🎉 **Готово! Твой бот теперь работает на удалённом сервере!**
