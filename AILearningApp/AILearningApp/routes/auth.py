
from flask import request, render_template, redirect, url_for, flash
from werkzeug.security import check_password_hash

from AILearningApp.models import User

from werkzeug.security import generate_password_hash

from AILearningApp.services.mail_service import send_reset_email
from AILearningApp.services.token_service import create_reset_token


from AILearningApp import app
from AILearningApp.db import get_connection
from AILearningApp.forms import RegisterForm, LoginForm,PasswordResetForm, PasswordChangeForm
from flask_login import login_user, logout_user, current_user

from datetime import datetime




@app.route("/")
def index():

    if current_user.is_authenticated:
        return redirect("/questions")

    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()


    if form.validate_on_submit():

        user_name = form.user_name.data
        email = form.email.data
        password = form.password.data


        password_hash = generate_password_hash(password)


        conn = get_connection()
        cur = conn.cursor()


        cur.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cur.fetchone()


        if existing_user:

            cur.close()
            conn.close()

            flash(
                "このメールアドレスはすでに登録されています"
            )

            return render_template(
                "register.html",
                form=form
            )


        cur.execute(
            """
            INSERT INTO users
            (
                user_name,
                email,
                password_hash
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                user_name,
                email,
                password_hash
            )
        )


        conn.commit()

        cur.close()
        conn.close()


        return redirect("/login")


    return render_template(
        "register.html",
        form=form
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    
    

    form = LoginForm()

    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                id,
                user_name,
                email,
                 password_hash,
                icon_filename
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        row = cur.fetchone()

        cur.close()
        conn.close()


        # ユーザー存在 + パスワード確認
        if row and check_password_hash(row[3], password):

            user = User(
            row[0],
            row[1],
            row[2],
            row[4]
        )
            login_user(user)

            return redirect("/questions")


        # ログイン失敗
        flash(
            "メールアドレスまたはパスワードが違います",
            "error"
        )

        return redirect(url_for("login"))


    return render_template(
        "login.html",
        form=form
    )

@app.route("/logout")
def logout():
    logout_user()
     
    return redirect("/login")



@app.route("/password_reset", methods=["GET", "POST"])
def password_reset():

    form = PasswordResetForm()


    if form.validate_on_submit():

        email = form.email.data

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, user_name FROM users WHERE email = %s"
            , (email,)
         )

        user = cur.fetchone()



        

        # 登録しているメールアドレスが存在しない場合
        if not user:

            cur.close()
            conn.close()

            flash("メールを送信しました",
                    "success"
                    )
            
            print("送信失敗")
            return redirect(url_for("login"))
        
        flash("メールを送信しました",
                    "success"
                    )

        token = create_reset_token(user[0])

        cur.close()
        conn.close()

        send_reset_email(email, user[1], token)

        

        print("送信成功")
        return redirect(url_for("login"))

    return render_template(
        "password_reset.html",
        form=form
    )


@app.route("/password_change/<token>", methods=["GET", "POST"])
def password_change(token):

    form = PasswordChangeForm()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, expires_at, used
        FROM password_reset_tokens
        WHERE token = %s
    """, (token,))

    row = cur.fetchone()

    


    # トークンが存在しない場合
    if not row:
        

        cur.close()
        conn.close()
        flash("このリンクは無効です。", "success")
        return redirect(url_for("login"))

    user_id, expires_at, used = row


    # トークンが使用済み、または有効期限切れ
    if used or expires_at < datetime.now():
        cur.close()
        conn.close()
        flash("このリンクは無効です。", "success")
        return redirect(url_for("login"))

    if form.validate_on_submit():

        new_password = form.password.data
        hashed_password = generate_password_hash(new_password)

        post_conn = get_connection()
        post_cur = post_conn.cursor()

        post_cur.execute("""
            UPDATE users
            SET password_hash = %s
            WHERE id = %s
        """, (hashed_password, user_id))

        post_cur.execute("""
            UPDATE password_reset_tokens
            SET used = TRUE
            WHERE token = %s
        """, (token,))

        post_conn.commit()

        post_cur.close()
        post_conn.close()

        flash("パスワードを変更しました。新しいパスワードでログインしてください。", "success")

        return redirect(url_for("login"))
    cur.close()
    conn.close()

    

    return render_template(
        "password_change.html",
        form=form,
        token=token
    )
