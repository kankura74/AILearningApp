from flask_login import UserMixin


class User(UserMixin):

    def __init__(
        self,
        id,
        user_name,
        email,
        icon_filename
    ):
        self.id = id
        self.user_name = user_name
        self.email = email
        self. icon_filename = icon_filename