import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def connect_db():
    return sqlite3.connect("users.db")

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли таблица users
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            # Создаем таблицу users, если она не существует
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    joined_date TEXT,
                    last_activity TEXT
                )
            ''')
        else:
            # Проверяем, существуют ли столбцы joined_date и last_activity
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            # Добавляем столбцы, если их нет
            if 'joined_date' not in column_names:
                cursor.execute('ALTER TABLE users ADD COLUMN joined_date TEXT')
            
            if 'last_activity' not in column_names:
                cursor.execute('ALTER TABLE users ADD COLUMN last_activity TEXT')
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    
    # Создаем таблицу для статистики
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            user_id INTEGER,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Проверяем, существует ли пользователь
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            # Если пользователя нет, добавляем его
            cursor.execute('INSERT INTO users (id, joined_date, last_activity) VALUES (?, ?, ?)', 
                          (user_id, now, now))
        else:
            # Если пользователь уже существует, обновляем last_activity
            cursor.execute('UPDATE users SET last_activity = ? WHERE id = ?', (now, user_id))
        
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error adding/updating user {user_id}: {e}")
    finally:
        conn.close()

def log_action(action, user_id):
    conn = connect_db()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO statistics (action, user_id, timestamp) VALUES (?, ?, ?)', 
                  (action, user_id, now))
    conn.commit()
    conn.close()

def get_all_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users')
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]

def get_statistics():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Общее количество пользователей
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # Количество активных пользователей за последние 7 дней
    cursor.execute("SELECT COUNT(*) FROM users WHERE datetime(last_activity) > datetime('now', '-7 days')")
    active_users = cursor.fetchone()[0]
    
    # Количество использований команды /start
    cursor.execute("SELECT COUNT(*) FROM statistics WHERE action = 'start'")
    start_count = cursor.fetchone()[0]
    
    # Количество нажатий на кнопку "Выбрать подарок"
    cursor.execute("SELECT COUNT(*) FROM statistics WHERE action = 'get_guide'")
    guide_clicks = cursor.fetchone()[0]
    
    # Количество рассылок
    cursor.execute("SELECT COUNT(*) FROM statistics WHERE action = 'broadcast'")
    broadcast_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "start_count": start_count,
        "guide_clicks": guide_clicks,
        "broadcast_count": broadcast_count
    }