from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv

import os
load_dotenv()

app = Flask(__name__)





UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT"))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS") == "True"

app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")




# Flask-Mail起動
mail = Mail(app)



# Flask-Login設定
login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"



from AILearningApp.models import User
from AILearningApp.db import get_connection


import AILearningApp.views

import AILearningApp.routes.auth
import AILearningApp.routes.question
import AILearningApp.routes.history
import AILearningApp.routes.mypage



@login_manager.user_loader
def load_user(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            user_name,
            email,
            icon_filename
        FROM users
        WHERE id = %s
        """,
        (user_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:

        return User(
            row[0],
            row[1],
            row[2],
            row[3]
        )

    return None