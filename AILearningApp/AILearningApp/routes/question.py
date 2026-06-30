from flask import render_template
from flask_login import (
    login_required,
    current_user
)

from AILearningApp import app
from AILearningApp.db import get_connection

from flask import (
    request,
    redirect
    )

from AILearningApp.services.ai_service import (
    evaluate_answer
)

#問題一覧ページ


@app.route("/questions")
@login_required
def questions():

    category_id = request.args.get("category_id")
    difficulty = request.args.get("difficulty")
    conn = get_connection()
    cur = conn.cursor()

    # カテゴリ一覧取得
    cur.execute(
        """
        SELECT
            id,
            category_name
            FROM categories
            ORDER BY id
        """
    )

    categories = cur.fetchall()

    # 問題一覧取得
    sql = """
        SELECT
            q.id,
            q.title,
            c.category_name,
            q.difficulty,
            ah.result

        FROM questions q

        INNER JOIN categories c
            ON q.category_id = c.id

        LEFT JOIN (
            SELECT DISTINCT ON (question_id)
                question_id,
                result,
                answered_at
            FROM answer_histories
            WHERE user_id = %s
            ORDER BY question_id, answered_at DESC
        ) ah

        ON q.id = ah.question_id
    """

    params = [current_user.id]


    # カテゴリ検索
    if category_id:

        sql += """
            WHERE q.category_id = %s
        """

        params.append(category_id)


    # 難易度検索
    if difficulty:

        if category_id:
            sql += """
                AND q.difficulty = %s
            """
        else:
            sql += """
                WHERE q.difficulty = %s
            """

        params.append(difficulty)


    sql += """
        ORDER BY q.id
    """


    cur.execute(
        sql,
        tuple(params)
    )


    rows = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "questions.html",
        rows=rows,
        categories=categories
    )


#問題回答ページ
@app.route("/question/<int:question_id>", methods = ["GET", "POST"])
@login_required
def question_detail(question_id):

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":

        answer_code = request.form["answer_code"]

        cur.execute(
            """
            SELECT
                q.id,
                q.title,
                q.question_text,
                c.category_name,
                q.difficulty
            FROM questions q
            INNER JOIN categories c
                ON q.category_id = c.id
            WHERE q.id = %s
            """,
            (question_id,)
        )

        question_row = cur.fetchone()

        result = evaluate_answer(
        question_row[2],
        answer_code
        )

        print(result)

        cur.execute(
    """
    INSERT INTO answer_histories
    (
        user_id,
        question_id,
        answer_code,
        result,
        score,
        good_points,
        mistakes,
        improvement
    )
    VALUES
    (
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    )
    """,
    (
        current_user.id,
        question_id,
        answer_code,
        result["result"],
        result["score"],
        result["good_points"],
        result["mistakes"],
        result["improvement"]
    )
)
        
        

        conn.commit()

        cur.execute("SELECT MAX(id) FROM questions")
        max_id_row = cur.fetchone()

        max_id = max_id_row[0] if max_id_row[0] else 1


        cur.close()
        conn.close()


        return render_template(
            "result.html",
            result=result,
            question=question_row,
            answer_code=answer_code,
            max_id=max_id
        )

    cur.execute(
        """
        SELECT
            q.id,
            q.title,
            q.question_text,
            c.category_name,
            q.difficulty
        FROM questions q
        INNER JOIN categories c
            ON q.category_id = c.id
        WHERE q.id = %s
        """,
        (question_id,)
    )

    row = cur.fetchone()

    cur.execute("SELECT MAX(id) FROM questions")
    max_id_row = cur.fetchone()
    # データがない場合の安全策として1を初期値にする
    max_id = max_id_row[0] if max_id_row else 1 

    cur.close()
    conn.close()

    return render_template(
        "question.html",
        row=row,
        max_id=max_id
    )

