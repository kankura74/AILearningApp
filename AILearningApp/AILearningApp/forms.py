from flask_wtf import FlaskForm



from wtforms import (
    StringField,
    PasswordField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo
)

# 会員登録

class RegisterForm(FlaskForm):

    user_name = StringField(
        "ユーザー名",
        validators=[
            DataRequired(
                message="ユーザー名を入力してください"
            ),
            Length(
                max=20,
                message="ユーザー名は20文字以内で入力してください"
            )
        ]
    )


    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired(
                message="メールアドレスを入力してください"
            ),
            Email(
                message="正しいメールアドレスを入力してください"
            )
        ]
    )


    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired(
                message="パスワードを入力してください"
            ),
            Length(
                min=8,
                message="パスワードは8文字以上にしてください"
            )
        ]
    )


    password_confirm = PasswordField(
        "パスワード確認",
        validators=[
            DataRequired(
                message="パスワード確認を入力してください"
            ),
            EqualTo(
                "password",
                message="パスワードが一致しません"
            )
        ]
    )


    submit = SubmitField("登録")




# ログイン

class LoginForm(FlaskForm):

    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired(
                message="メールアドレスを入力してください"
            ),
            Email(
                message="正しいメールアドレスを入力してください"
            )
        ]
    )


    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired(
                message="パスワードを入力してください"
            )
        ]
    )


    submit = SubmitField("ログイン")


    # パスワード関係

class PasswordResetForm(FlaskForm):

    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired(
                message="メールアドレスを入力してください"
            ),
            Email(
                message="正しいメールアドレスを入力してください"
            )
        ]
    )


    submit = SubmitField("送信")


# パスワード変更画面




class PasswordChangeForm(FlaskForm):
    password = PasswordField(
        "新しいパスワード",
        validators=[
            DataRequired(message="パスワードを入力してください"),
            Length(min=8, message="パスワードは8文字以上にしてください")
        ]
    )

    password_confirm = PasswordField(
        "パスワード確認",
        validators=[
            DataRequired(message="パスワード確認を入力してください"),
            EqualTo("password", message="パスワードが一致しません")
        ]
    )

    submit = SubmitField("変更する")