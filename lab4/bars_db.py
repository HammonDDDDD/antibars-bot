import sqlite3
from typing import Dict, Optional
from lab4.constants import DATABASE_FILE


def init_db() -> None:
    """
    Initialize the database by creating necessary tables if they don't exist.
    
    This method ensures the database schema is properly set up to support 
    the bot's notification and tracking functionality. It creates tables 
    for managing user subscriptions and maintaining change history for 
    debugging and monitoring purposes.
    
    Args: None
    
    Returns: None
    """
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
    """
    Add a subscription mapping an identifier to a chat_id.
    
    This method ensures that a specific identifier (which could represent a user or entity) 
    is associated with a Telegram chat ID in the database. If an existing subscription 
    for the identifier already exists, it will be replaced with the new chat_id.
    
    Args:
        identifier (str): The identifier (e.g., user ID or name) to subscribe.
        chat_id (int): The Telegram chat ID to associate with the identifier.
    
    Returns:
        bool: True if the subscription was successfully added or updated, False otherwise.
    """
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
    """
    Retrieve the chat_id associated with a given identifier from the database.
    
    This method enables the bot to look up the Telegram chat ID for a specific user or entity identifier, which is essential for directing notifications and updates to the correct recipient.
    
    Args:
        identifier (str): The unique identifier (e.g., ISU number or full name) used to look up the chat_id.
    
    Returns:
        Optional[int]: The chat_id if found, otherwise None if no matching record exists or an error occurs.
    """
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
    """
    Retrieve all active subscriptions from the database as a mapping of identifiers to chat IDs.
    
    This method provides a complete view of currently subscribed users and their associated chat identifiers,
    enabling the system to efficiently route notifications and updates to the appropriate Telegram chats.
    
    Args:
        None
    
    Returns:
        Dict[str, int]: A dictionary where keys are unique identifiers and values are Telegram chat IDs.
                       Returns an empty dictionary if an error occurs or no subscriptions exist.
    """
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
    """
    Logs a change to the database for tracking and debugging purposes.
    
    This method records changes made to specific columns in database tables,
    creating an audit trail that can be used for debugging, monitoring data modifications,
    and maintaining data integrity.
    
    Args:
        table_id: The identifier of the table where the change occurred
        identifier: The unique identifier of the record that was modified
        column_name: The name of the column that was changed
        old_value: The previous value of the column before modification
        new_value: The new value of the column after modification
    
    Returns:
        None
    """
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
