from datetime import datetime
from hashlib import md5
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

PASSWORD ="root"
PUBLIC_IP_ADDRESS ="34.90.67.52"
DBNAME ="datab"
PROJECT_ID ="gatest-315020"
INSTANCE_NAME ="test1"
  

def gen_connection_string():
    # if not on Google then use local MySQL
    if not os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        return 'mysql://root@localhost/blog'
    else:
        conn_name = os.environ.get('CLOUDSQL_CONNECTION_NAME' '')
        sql_user = os.environ.get('CLOUDSQL_USER', 'root')
        sql_pass = os.environ.get('CLOUDSQL_PASSWORD', '')
        conn_template = 'mysql+mysqldb://%s:%s@/blog?unix_socket=/cloudsql/%s'
        return conn_template % (sql_user, sql_pass, conn_name)

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = gen_connection_string()
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140), index=True, unique=True)
    url = db.Column(db.String(140))
    datai = db.Column(db.JSON(366),nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.datai)
