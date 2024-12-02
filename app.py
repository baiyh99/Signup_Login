from flask import Flask, request, jsonify, json, session
from models import db, teacher_posts, student_posts, user_register

from extension import db, cors
from flask_cors import CORS
# from users import userInfo
from indexPage import indexpage
from teacher_postings import teacher_postings
from student_postings import student_postings
from add_teacher_posts import add_teacher_posts
from add_student_posts import add_student_posts





def createApp():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    # SQL setup 之后需要再修改SQL地址
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Jbsd93233%@localhost/UserInfo'
    sqlEngine = app.config['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    CORS(app)
    app.secret_key = 'super secret key'

    app.register_blueprint(indexpage, url_prefix='/')
    app.register_blueprint(teacher_postings, url_prefix='/search_results1')
    app.register_blueprint(student_postings, url_prefix='/search_results0')
    app.register_blueprint(add_teacher_posts, url_prefix='/add_post1')
    app.register_blueprint(add_student_posts, url_prefix='/add_post0')
    return app

app = createApp()


            
# class user_register(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     fullname = db.Column(db.String(80), nullable=False)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     user_password = db.Column(db.String(120), nullable=False)
#     phone = db.Column(db.String(120), unique=True, nullable=False)
    
#    


#------------------------------------------------------------
# shell里输入flask recreate重置用户注册信息数据表
@app.cli.command('recreate')
def create():
    db.drop_all()
    db.create_all()

@app.cli.command('recreateTeacher')
def drop_teacher_posts():
    db.session.remove()
    teacher_posts.__table__.drop(db.engine, checkfirst=True)
    db.create_all()

@app.cli.command('recreateStudent')
def drop_teacher_posts():
    db.session.remove()
    student_posts.__table__.drop(db.engine, checkfirst=True)
    db.create_all()

@app.cli.command('recreateUsers')
def drop_registerUsers():
    db.session.remove()
    user_register.__table__.drop(db.engine, checkfirst=True)
    db.create_all()







#----------------------------

if __name__ == "__main__":
    app.run(debug = True)
