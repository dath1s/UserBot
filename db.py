import sqlite3


def create_sqlite_database(filename: str):
    conn = None
    try:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Requests (
            id INTEGER PRIMARY KEY,
            user_tg_id INTEGER NOT NULL,
            filepath TEXT NOT NULL DEFAULT '-',
            message TEXT NOT NULL DEFAULT '-',
            delay REAL NOT NULL DEFAULT '0'
            )
        ''')
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def create_request(user_id: int, filepath: str) -> None:
    create_sqlite_database('requests.db')
    conn = sqlite3.connect('requests.db')
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Requests (user_tg_id, filepath) VALUES (?, ?)',
            (user_id, str(filepath))
        )
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def add_message(user_id: int, message: str):
    conn = sqlite3.connect('requests.db')
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE Requests SET message = '{message}' "
            f"WHERE user_tg_id = {user_id} and id = (SELECT MAX(id) FROM Requests WHERE user_tg_id = {user_id})"
        )
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def add_delay(user_id: int, delay: float):
    conn = sqlite3.connect('requests.db')
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE Requests SET delay = {delay} "
            f"WHERE user_tg_id = {user_id} and id = (SELECT MAX(id) FROM Requests WHERE user_tg_id = {user_id})"
        )
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def get_data(user_id: int):
    conn = sqlite3.connect('requests.db')
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM Requests WHERE user_tg_id = {user_id}"
        )
        _, _, filepath, mes, delay = cursor.fetchall()[-1]
        delay = float(delay)

        return filepath, mes, delay
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return '', '-', 0
