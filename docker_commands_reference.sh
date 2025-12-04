#!/bin/bash
# 📜 Примеры команд Docker и Docker Compose для управления ботом

# =====================================================
# 🔧 ОСНОВНЫЕ КОМАНДЫ
# =====================================================

# Сборка образа (один раз при первом деплое или после обновления кода)
docker-compose build

# Запуск контейнера в фоновом режиме
docker-compose up -d

# Запуск контейнера с выводом логов (для тестирования)
docker-compose up

# Остановка контейнера
docker-compose down

# Перезапуск контейнера
docker-compose restart

# =====================================================
# 📊 ПРОСМОТР ЛОГОВ
# =====================================================

# Все логи с начала
docker-compose logs antibars-bot

# Последние 100 строк
docker-compose logs --tail=100 antibars-bot

# Логи в реальном времени (live follow)
docker-compose logs -f antibars-bot

# Логи с временными метками
docker-compose logs --timestamps antibars-bot

# Выход из логов: Ctrl+C

# =====================================================
# 🔍 МОНИТОРИНГ И СТАТУС
# =====================================================

# Показать статус контейнеров
docker-compose ps

# Подробная информация о контейнерах
docker-compose ps -a

# Использование ресурсов (CPU, память, сеть)
docker stats antibars-bot

# =====================================================
# 🛠️ ОТЛАДКА И ДИАГНОСТИКА
# =====================================================

# Вход в shell контейнера
docker-compose exec antibars-bot bash

# Запуск Python в контейнере
docker-compose exec antibars-bot python3

# Проверка файловой системы контейнера
docker-compose exec antibars-bot ls -la /app/data

# Проверка БД SQLite
docker-compose exec antibars-bot sqlite3 data/bars_db.sqlite ".tables"

# Проверка всех таблиц в БД
docker-compose exec antibars-bot sqlite3 data/bars_db.sqlite ".schema"

# Просмотр подписчиков
docker-compose exec antibars-bot sqlite3 data/bars_db.sqlite "SELECT * FROM subscriptions;"

# Просмотр истории изменений
docker-compose exec antibars-bot sqlite3 data/bars_db.sqlite "SELECT * FROM change_history LIMIT 10;"

# Очистка БД (осторожно!)
# docker-compose exec antibars-bot rm data/bars_db.sqlite

# =====================================================
# 🔄 ОБНОВЛЕНИЕ КОДА
# =====================================================

# Обновляем код с GitHub
git pull

# Пересобираем образ с новым кодом
docker-compose build --no-cache

# Перезапускаем контейнер
docker-compose restart

# Или остановка и запуск с новым образом
docker-compose down
docker-compose up -d

# Проверяем логи новой версии
docker-compose logs -f antibars-bot

# =====================================================
# 🧹 ОЧИСТКА И УДАЛЕНИЕ
# =====================================================

# Удаление остановленных контейнеров
docker container prune

# Удаление неиспользуемых образов
docker image prune

# Удаление образа бота
docker rmi antibars-bot:latest

# Удаление всех контейнеров, образов, volumes (полная очистка)
docker-compose down -v

# =====================================================
# 💾 BACKUP И ВОССТАНОВЛЕНИЕ
# =====================================================

# Backup БД (внутри контейнера)
docker-compose exec antibars-bot cp data/bars_db.sqlite data/bars_db.sqlite.backup

# Копирование БД на локальную машину
docker cp $(docker-compose ps -q antibars-bot):/app/data/bars_db.sqlite ./backup/

# Копирование БД с сервера на локальную машину (по SSH)
scp user@server.com:/opt/antibars-bot/data/bars_db.sqlite ./backup/

# Копирование локального БД в контейнер
docker cp ./backup/bars_db.sqlite $(docker-compose ps -q antibars-bot):/app/data/

# =====================================================
# 📝 ДОКУМЕНТАЦИЯ DOCKER
# =====================================================

# Справка по docker-compose
docker-compose --help

# Справка по конкретной команде
docker-compose up --help

# =====================================================
# 🚨 РЕШЕНИЕ ПРОБЛЕМ
# =====================================================

# Проверка сетевого подключения контейнера
docker-compose exec antibars-bot ping google.com

# Проверка переменных окружения в контейнере
docker-compose exec antibars-bot env

# Проверка процессов в контейнере
docker-compose exec antibars-bot ps aux

# Проверка, что файл credentials на месте
docker-compose exec antibars-bot ls -la data/antibars-credentials.json

# Просмотр конфигурации Docker Compose
docker-compose config

# =====================================================
# ⚡ БЫСТРЫЕ КОМАНДЫ
# =====================================================

# Перезагрузиться и проверить логи
docker-compose restart && sleep 2 && docker-compose logs -f antibars-bot

# Пересобрать и запустить с логами
docker-compose build --no-cache && docker-compose up

# Удалить всё и начать заново
docker-compose down -v && docker-compose build && docker-compose up -d

# =====================================================
# 🎯 ПРАКТИЧЕСКИЕ ПРИМЕРЫ
# =====================================================

# Сценарий 1: Первый деплой на сервер
: '
1. mkdir -p /opt/antibars-bot
2. cd /opt/antibars-bot
3. # Копируем файлы проекта
4. docker-compose build
5. mkdir -p data
6. cp antibars-credentials.json data/
7. cp .env.example .env && nano .env
8. docker-compose up -d
9. docker-compose logs -f antibars-bot
'

# Сценарий 2: Обновление кода
: '
1. cd /opt/antibars-bot
2. git pull
3. docker-compose build --no-cache
4. docker-compose restart
5. docker-compose logs -f antibars-bot
'

# Сценарий 3: Отладка падения контейнера
: '
1. docker-compose logs --tail=50 antibars-bot  # Смотрим логи
2. docker-compose exec antibars-bot bash        # Входим в контейнер
3. python3 -m lab4.async_bot                    # Пытаемся запустить вручную
4. exit
'

# Сценарий 4: Резервное копирование
: '
1. docker-compose exec antibars-bot cp data/bars_db.sqlite data/backup_$(date +%Y%m%d).sqlite
2. docker cp $(docker-compose ps -q antibars-bot):/app/data/backup_*.sqlite ./local_backup/
3. # Отправляем на облако через scp, rsync или другие инструменты
'

# =====================================================
# 📚 ПОЛЕЗНЫЕ КОМБИНАЦИИ
# =====================================================

# Отправить логи в файл
docker-compose logs antibars-bot > bot_logs_$(date +%Y%m%d_%H%M%S).txt

# Получить IP адрес контейнера
docker-compose exec antibars-bot hostname -I

# Время, сколько работает контейнер
docker-compose ps

# Объем использованного диска
du -sh data/

# Количество активных подписчиков
docker-compose exec antibars-bot sqlite3 data/bars_db.sqlite "SELECT COUNT(*) FROM subscriptions;"

# =====================================================
# 🔐 БЕЗОПАСНОСТЬ
# =====================================================

# Просмотр .env (осторожно с токенами!)
cat .env

# Просмотр логов без чувствительных данных
docker-compose logs antibars-bot | grep -v "BOT_TOKEN"

# Проверка прав доступа к файлам
ls -la data/

# Установка правильных прав (для credentials)
chmod 600 data/antibars-credentials.json
chmod 644 requirements.txt
