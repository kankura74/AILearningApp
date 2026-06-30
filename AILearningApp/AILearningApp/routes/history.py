from flask import render_template
from flask_login import login_required, current_user

from AILearningApp import app
from AILearningApp.db import get_connection


@app.route("/history")
@login_required
def history_list():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            ah.id,
            q.title,
            ah.result,
            ah.score,
            ah.answered_at
        FROM answer_histories ah
        JOIN questions q
            ON ah.question_id = q.id
        WHERE ah.user_id = %s
        ORDER BY ah.id DESC
        """,
        (current_user.id,)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "history.html",
        rows=rows
    )

@app.route("/history/<int:history_id>")
@login_required
def history_detail(history_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            ah.id,
            q.title,
            q.question_text,
            ah.answer_code,
            ah.result,
            ah.score,
            ah.good_points,
            ah.mistakes,
            ah.improvement,
            ah.answered_at
        FROM answer_histories ah
        JOIN questions q ON ah.question_id = q.id
        WHERE ah.id = %s
        AND ah.user_id = %s
        """,
        (history_id, current_user.id)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "history_detail.html",
        row=row
    )