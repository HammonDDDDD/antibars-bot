# ❓ FAQ: Часто задаваемые вопросы о Docker деплое

## 🆘 Проблемы при запуске

### Q: Контейнер падает сразу после запуска
**A:**
```bash
# Смотрим логи ошибки
docker-compose logs antibars-bot

# Типичные ошибки:
# 1. "No such file" - нет файла antibars-credentials.json
# 2. "Invalid token" - неправильный BOT_TOKEN в .env
# 3. "Connection refused" - нет интернета на сервере
# 4. "Module not found" - не установлена зависимость
```

Решение:
```bash
# Проверяем credentials
ls -la data/antibars-credentials.json

# Проверяем .env
cat .env

# Проверяем интернет внутри контейнера
docker-compose exec antibars-bot ping 8.8.8.8
```

---

### Q: Ошибка "Cannot connect to Google Sheets API"
**A:**
```bash
# Проверяем, что credentials на месте
docker-compose exec antibars-bot ls -la /app/data/antibars-credentials.json

# Проверяем путь в constants.py
docker-compose exec antibars-bot grep GOOGLE_SHEETS_CREDENTIALS_FILE lab4/constants.py
```

Если путь неправильный, отредактируй `constants.py`:
```python
# Должно быть:
GOOGLE_SHEETS_CREDENTIALS_FILE = "/app/data/antibars-credentials.json"
# Или просто:
GOOGLE_SHEETS_CREDENTIALS_FILE = "antibars-credentials.json"
```

Затем пересобери:
```bash
docker-compose build --no-cache
docker-compose restart
```

---

### Q: Ошибка "Resource is read-only" при записи в БД
**A:**
```bash
# Проверяем права доступа
docker-compose exec antibars-bot ls -la data/

# Если БД недоступна, переходим в контейнер
docker-compose exec antibars-bot bash

# Удаляем старую БД (она пересоздастся)
rm data/bars_db.sqlite

# Выходим и перезапускаем
exit
docker-compose restart
```

---

### Q: "Telegram API: (401) Unauthorized"
**A:** BOT_TOKEN неправильный!

```bash
# Проверяем токен в .env
cat .env

# Убедись, что это правильный токен из @BotFather
# Он должен быть в виде: 123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh

# Обновляем .env
nano .env

# Пересобираем
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 💻 Вопросы о командах

### Q: Как запустить бот в интерактивном режиме (для тестирования)?
**A:**
```bash
# Вместо -d (detach), просто запускаем без флага
docker-compose up

# Видишь логи в реальном времени
# Нажми Ctrl+C чтобы остановить (не пугайся, это нормально)
```

---

### Q: Как получить доступ к Python shell внутри контейнера?
**A:**
```bash
# Открыть Python интерпретатор
docker-compose exec antibars-bot python3

# Теперь можешь писать Python код
>>> print("Hello from container!")
>>> import asyncio
>>> exit()
```

---

### Q: Как отредактировать файл внутри контейнера?
**A:**
```bash
# Входим в bash контейнера
docker-compose exec antibars-bot bash

# Редактируем файл (если nano установлен)
nano lab4/constants.py

# Или используем cat и echo
echo "новое значение" > data/config.txt

# Выходим
exit

# Перезапускаем контейнер с новыми значениями
docker-compose restart
```

---

### Q: Как проверить, что БД работает?
**A:**
```bash
# Входим в sqlite
docker-compose exec antibars-bot sqlite3 data/bars_db.sqlite

# Теперь ты в SQLite интерпретаторе
> .tables  # Показывает все таблицы
> SELECT * FROM subscriptions;  # Показывает подписчиков
> .quit  # Выходим
```

---

### Q: Как отправить файл с сервера на локальную машину?
**A:**
```bash
# С локальной машины
scp user@server.com:/opt/antibars-bot/data/bars_db.sqlite ./local_backup/

# Или весь архив
scp -r user@server.com:/opt/antibars-bot/ ./backup-from-server/
```

---

## 🔧 Оптимизация и производительность

### Q: Контейнер использует слишком много памяти
**A:**
```bash
# Проверяем текущее использование
docker stats antibars-bot

# Если не помещается в лимиты, измени docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 512M  ← увеличиваем тут

docker-compose down
docker-compose up -d
```

---

### Q: Как уменьшить размер образа?
**A:**

В Dockerfile используй многоэтапную сборку:
```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "-m", "lab4.async_bot"]
```

Пересобири:
```bash
docker-compose build --no-cache
```

---

### Q: Как ускорить перезагрузку после изменения кода?
**A:**
```bash
# Быстрый способ (если не менялись зависимости)
git pull
docker-compose build --no-cache
docker-compose restart

# Супер быстрый (если менялась логика, но не импорты)
# Просто перезапусти контейнер
docker-compose restart
```

---

## 🔒 Безопасность

### Q: Как защитить BOT_TOKEN?
**A:**
```bash
# 1. Используй .env (не коммитим в git)
echo ".env" >> .gitignore
git rm --cached .env  # Если уже закоммитили

# 2. Используй .gitignore
# .env
# data/antibars-credentials.json
# .env.local
# .env.*.local

# 3. На продакшене используй Docker Secrets или инструменты вроде Vault
```

---

### Q: Как сделать автоматический backup?
**A:**
```bash
# Создай скрипт backup.sh
#!/bin/bash
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR

# Backup БД
docker-compose exec antibars-bot cp data/bars_db.sqlite data/backup_$(date +%Y%m%d).sqlite
docker cp $(docker-compose ps -q antibars-bot):/app/data/backup_*.sqlite $BACKUP_DIR/

# Удаляем старые backups (старше 7 дней)
find $BACKUP_DIR -name "backup_*.sqlite" -mtime +7 -delete

echo "Backup completed at $(date)"

# Затем добавь в crontab (запуск каждый день в 3:00)
# 0 3 * * * /opt/backup.sh
```

Дай права:
```bash
chmod +x backup.sh
sudo crontab -e
# Добавь: 0 3 * * * /opt/antibars-bot/backup.sh
```

---

## 📊 Мониторинг

### Q: Как настроить уведомления при падении контейнера?
**A:**

Используй `healthcheck` в docker-compose.yml:
```yaml
services:
  antibars-bot:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Или проверяй через shell скрипт:
```bash
#!/bin/bash
if ! docker-compose ps | grep "antibars-bot.*Up"; then
  echo "Bot is down!" | mail -s "Alert" your@email.com
  docker-compose restart
fi
```

Добавь в crontab:
```bash
*/5 * * * * /opt/check-bot.sh
```

---

### Q: Как собирать метрики?
**A:**

Используй Prometheus + Grafana или просто читай из docker stats:
```bash
# Периодически сохраняй метрики
watch -n 60 'docker stats --no-stream antibars-bot >> metrics.log'

# Или создай скрипт
#!/bin/bash
echo "$(date),$(docker stats --no-stream antibars-bot --format '{{.CPUPerc}},{{.MemUsage}}')" >> docker_metrics.csv
```

---

## 🚀 Расширенное использование

### Q: Как использовать несколько ботов в одном docker-compose?
**A:**
```yaml
version: '3.9'

services:
  antibars-bot:
    build: .
    container_name: antibars-bot
    # ...

  another-bot:
    build:
      context: ./another-bot
      dockerfile: Dockerfile
    container_name: another-bot
    # ...
```

Затем:
```bash
docker-compose up -d  # Запустит оба
docker-compose logs antibars-bot  # Логи первого
docker-compose logs another-bot   # Логи второго
```

---

### Q: Как использовать Docker для локальной разработки?
**A:**
```bash
# Запускаешь контейнер в интерактивном режиме
docker-compose run --rm antibars-bot bash

# Теперь можешь тестировать код
python3 -m lab4.async_bot

# Или запусти python shell
python3

# Выход
exit
```

---

### Q: Как интегрировать с CI/CD (GitHub Actions)?
**A:**

Создай `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Server

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh user@server.com << 'EOF'
          cd /opt/antibars-bot
          git pull
          docker-compose build --no-cache
          docker-compose restart
          EOF
```

---

## 📚 Больше ресурсов

- [Docker Compose документация](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Python Docker Best Practices](https://docs.docker.com/language/python/build-images/)

---

## 💡 Полезные советы

1. **Всегда используй --no-cache при изменении кода:**
   ```bash
   docker-compose build --no-cache
   ```

2. **Сохраняй логи для отладки:**
   ```bash
   docker-compose logs antibars-bot > logs_backup.txt
   ```

3. **Используй .dockerignore как .gitignore:**
   ```
   __pycache__
   *.pyc
   .env
   .git
   ```

4. **Проверяй конфигурацию перед запуском:**
   ```bash
   docker-compose config  # Выведет всю конфигурацию
   ```

5. **Мониторь использование памяти:**
   ```bash
   watch -n 1 'docker stats --no-stream'
   ```

---

🎉 **Если ничего не помогает, всегда есть ядерная опция:**
```bash
docker-compose down -v
rm -rf data/
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f antibars-bot
```
