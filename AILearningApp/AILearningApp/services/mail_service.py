from flask_mail import Message
from AILearningApp import mail, app

def send_reset_email(email, username, token):
    reset_url = f"http://localhost:5000/password_change/{token}"

    msg = Message(
        subject="【AIコードチェッカー】パスワード再設定のご案内",
        recipients=[email]
    )

    msg.body = f"""
 {username} 様

「AIコードチェッカー」をご利用いただきありがとうございます。
パスワード再設定のリクエストを受け付けました。

下記のURLにアクセスし、新しいパスワードを設定してください。:

{reset_url}

※このURLの有効期限は、発行から30分です。
※お心当たりがない場合は、このメールを破棄してください。
　リンクを操作しない限り、パスワードは変更されません。
"""

    mail.send(msg)