from flask import request, redirect, render_template, flash, url_for
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from AILearningApp import app
from AILearningApp.db import get_connection
from AILearningApp.services.image_service import save_icon
from datetime import date, datetime, timedelta
from AILearningApp.services.ai_service import generate_learning_comment


@app.route("/mypage")
@login_required
def mypage():
    conn = get_connection()
    cur = conn.cursor()

    # 総回答数
    cur.execute(
        """
        SELECT COUNT(*)
        FROM answer_histories
        WHERE user_id = %s
        AND result IN ('OK', 'NG')
        """,
        (current_user.id,)
    )
    total_count = cur.fetchone()[0]

    # 平均スコア
    cur.execute(
        """
        SELECT AVG(score)
        FROM answer_histories
        WHERE user_id = %s
        AND result IN ('OK', 'NG')
        """,
        (current_user.id,)
    )
    avg_score = cur.fetchone()[0]

    # OK数
    cur.execute(
        """
        SELECT COUNT(*)
        FROM answer_histories
        WHERE user_id = %s
        AND result = 'OK'
        """,
        (current_user.id,)
    )
    ok_count = cur.fetchone()[0]

    # NG数
    cur.execute(
        """
        SELECT COUNT(*)
        FROM answer_histories
        WHERE user_id = %s
        AND result = 'NG'
        """,
        (current_user.id,)
    )
    ng_count = cur.fetchone()[0]

    # 利用開始月取得のためにcreated_atのみDBから取得（他のユーザー情報はcurrent_userで賄うため削減）
    cur.execute("SELECT created_at FROM users WHERE id=%s", (current_user.id,))
    created_at = cur.fetchone()[0]
    start_month = created_at.strftime("%Y-%m")

    # カレンダー用：日別学習数取得
    cur.execute(
        """
        SELECT 
            DATE(answered_at),
            COUNT(*)
        FROM answer_histories
        WHERE user_id = %s
        AND result IN ('OK', 'NG')
        GROUP BY DATE(answered_at)
        ORDER BY DATE(answered_at)
        """,
        (current_user.id,)
    )
    study_rows = cur.fetchall()

        # 日付一覧（重複なし）
    study_days = sorted({row[0] for row in study_rows})

    total_days = len(study_days)
    current_streak = 0
    max_streak = 0

    if study_days:
        current_streak = 1
        max_streak = 1

        # 1. 過去の連続日数を計算
        for i in range(1, len(study_days)):
            if (study_days[i] - study_days[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1

        # 2. 【バグ修正】直近で学習しているかチェック
        today = date.today()
        latest_study_day = study_days[-1]
        
        # 最新の学習日が「今日」でも「昨日」でもなければ、現在の国数は0リセット
        if (today - latest_study_day).days > 1:
            current_streak = 0
            
    else:
        total_days = 0
        current_streak = 0
        max_streak = 0





    # JavaScriptへ渡しやすい形に変換
    # JavaScriptへ渡しやすい形に変換
    study_dates = {}
    for row in study_rows:
        dt_str = row[0].strftime("%Y-%m-%d")  # ⭕ 変数名を dt_str に変更
        study_dates[dt_str] = row[1]

    # AIコメント取得
    cur.execute(
        """
        SELECT ai_comment, ai_comment_updated_at
        FROM users
        WHERE id=%s
        """,
        (current_user.id,)
    )

    ai_row = cur.fetchone()


    # AI生成が必要か判断
    need_generate = False


    if ai_row[0] is None:
        # 初回
        need_generate = True

    elif ai_row[1] is None:
        need_generate = True

    else:
        # 1日以上経過したら更新
        if datetime.now() - ai_row[1] > timedelta(days=1):
            need_generate = True



    if need_generate:

        ai_message = generate_learning_comment(
            max_streak,
            current_streak,
            total_days
        )


        cur.execute(
            """
            UPDATE users
            SET ai_comment=%s,
                ai_comment_updated_at=%s
            WHERE id=%s
            """,
            (
                ai_message,
                datetime.now(),
                current_user.id
            )
        )

        conn.commit()


    else:

        ai_message = ai_row[0]

    cur.close()
    conn.close()

    

    return render_template(
        "mypage.html",
        total_count=total_count,
        avg_score=avg_score,
        ok_count=ok_count,
        ng_count=ng_count,
        study_dates=study_dates,
        start_month=start_month,
        num1=max_streak,
        num2=current_streak,
        num3=total_days,

        ai_message=ai_message 
    )


@app.route("/mypage/edit", methods=["GET", "POST"])
@login_required
def mypage_edit():
    if request.method == "POST":
        username = request.form["user_name"]
        email = request.form["email"]  # 追加したメールアドレス
        icon = request.files.get("icon")
        filename = None

        if icon:
            filename = save_icon(icon)

        conn = get_connection()
        cur = conn.cursor()

        if filename:
            cur.execute(
                """
                UPDATE users
                SET user_name=%s, email=%s, icon_filename=%s
                WHERE id=%s
                """,
                (username, email, filename, current_user.id)
            )
        else:
            cur.execute(
                """
                UPDATE users
                SET user_name=%s, email=%s
                WHERE id=%s
                """,
                (username, email, current_user.id)
            )

        conn.commit()
        cur.close()
        conn.close()

        # 変更を反映させるため、現在のセッション内の情報を同期、または再起動
        # (Flask-LoginのUserモデル定義によってはリダイレクト後に自動更新されます)
        return redirect("/mypage")

    # GET時はDBへの再クエリを完全に削除
    # すべての情報はテンプレート側で「current_user」から直接描画するため引数は空でOK
    return render_template("mypage_edit.html")


@app.route("/update-password", methods=["POST"])
@login_required
def update_password():
    current_password = request.form["current_password"]
    new_password = request.form["new_password"]

    conn = get_connection()
    cur = conn.cursor()

    # 現在のハッシュ化されたパスワードをDBから取得
    cur.execute("SELECT password_hash FROM users WHERE id=%s", (current_user.id,))
    row = cur.fetchone()
    
    # 既存のパスワードと合致するか検証
    if row and check_password_hash(row[0], current_password):
        # 新しいパスワードをハッシュ化して保存
        new_hash = generate_password_hash(new_password)
        cur.execute("UPDATE users SET password_hash=%s WHERE id=%s", (new_hash, current_user.id))
        conn.commit()
        flash("パスワードを変更しました。", "success")
    else:
        flash("現在のパスワードが正しくありません。", "error")

    cur.close()
    conn.close()
    return redirect("/mypage/edit")


@app.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    conn = get_connection()
    cur = conn.cursor()

    # 1. ユーザーに関連する解答履歴等の子レコードをすべて削除（制約がある場合に必要なため安全に実装）
    cur.execute("DELETE FROM answer_histories WHERE user_id=%s", (current_user.id,))
    cur.execute("DELETE FROM password_reset_tokens WHERE user_id=%s", (current_user.id,))  
    
    # 2. ユーザー本体の削除
    cur.execute("DELETE FROM users WHERE id=%s", (current_user.id,))
    
    conn.commit()
    cur.close()
    conn.close()

    # ログアウトさせてトップへリダイレクト
    logout_user()
    flash("アカウントを完全に削除しました。", "info")
    return redirect("/")
