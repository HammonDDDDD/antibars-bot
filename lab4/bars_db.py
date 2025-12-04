import sqlite3
from typing import Dict, Optional
from lab4.constants import DATABASE_FILE


def init_db() -> None:
    """Инициализировать БД (создать таблицы, если их нет)."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Таблица подписок: ИСУ/ФИО -> chat_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY,
            identifier TEXT UNIQUE NOT NULL,
            chat_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Таблица истории изменений (опционально, для отладки)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS change_history (
            id INTEGER PRIMARY KEY,
            table_id TEXT NOT NULL,
            identifier TEXT NOT NULL,
            column_name TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def add_subscription(identifier: str, chat_id: int) -> bool:
    """Добавить подписку (ИСУ/ФИО -> chat_id). Вернуть True если успешно."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO subscriptions "
            "(identifier, chat_id) VALUES (?, ?)",
            (identifier, chat_id),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding subscription: {e}")
        return False


def get_chat_id(identifier: str) -> Optional[int]:
    """Получить chat_id по ИСУ/ФИО."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT chat_id FROM subscriptions WHERE identifier = ?",
            (identifier,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"Error getting chat_id: {e}")
        return None


def get_all_subscriptions() -> Dict[str, int]:
    """Получить всех подписчиков как {identifier: chat_id}."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT identifier, chat_id FROM subscriptions")
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: row[1] for row in rows}
    except Exception as e:
        print(f"Error getting subscriptions: {e}")
        return {}


def log_change(
        table_id: str,
        identifier: str,
        column_name: str,
        old_value: str,
        new_value: str) -> None:
    """Логировать изменение для отладки."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO change_history
               (table_id, identifier, column_name, old_value, new_value)
               VALUES (?, ?, ?, ?, ?)""",
            (table_id, identifier, column_name, old_value, new_value),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging change: {e}")
