from extension import db
from werkzeug.security import generate_password_hash

PASSWORD_LENGTH = 20
USERNAME_LENGTH = 20
class userInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(USERNAME_LENGTH), unique=True, nullable=False)
    password_hash = db.Column(db.String(PASSWORD_LENGTH), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password) #encrypt