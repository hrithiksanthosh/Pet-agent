from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, username,password):
        self.id = username
        self.password = password

    def __repr__(self):
        return "%d/%s/%s" % ( self.id, self.password)

    def get_user(self,username):
        return self