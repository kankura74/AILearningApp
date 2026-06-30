import secrets
from datetime import datetime, timedelta
from AILearningApp.db import get_connection


def create_reset_token(user_id):

    conn = get_connection()
    cur = conn.cursor()

    try:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=30)

        cur.execute("""
            INSERT INTO password_reset_tokens
            (user_id, token, expires_at)
            VALUES (%s, %s, %s)
        """, (user_id, token, expires_at))

        conn.commit()

        return token

    finally:
        cur.close()
        conn.close()