from flask import render_template
from AILearningApp import app
from flask_login import login_required

from flask_login import login_required

from AILearningApp.db import get_connection




@app.route("/dbtest")
def dbtest():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("SELECT NOW();")

    result = cur.fetchone()

    cur.close()
    conn.close()

    return str(result)




