import psycopg2


def get_connection():

    conn = psycopg2.connect(
        host="localhost",
        database="ai_learning_app",
        user="postgres",
        password="sicadmin"
    )

    return conn