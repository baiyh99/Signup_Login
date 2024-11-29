from flask import Flask, render_template, request, flash, jsonify, json, session
from datetime import datetime, timedelta, timezone
from extension import db, cors
from flask_cors import CORS
from users import userInfo
import os, random
from sms_verification import userRegister
import time
import pytz

verificaiton_getTime = 0
verificationCode = ''
verifPhone = 0


def translateTimetoBeijing(utc_time):
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_time = utc_time.astimezone(beijing_tz)
    return beijing_time.replace(tzinfo=None)

def formatTimeStamp(postingTime):
        now = translateTimetoBeijing(datetime.now(pytz.utc))
        print(postingTime, now)
        time_diff = now - postingTime
        print(time_diff)
        if time_diff < timedelta(minutes=1):
            # 如果帖子发布时间在一分钟以内，显示“刚刚发布”
            return "刚刚发布"
        elif time_diff < timedelta(hours=1):
            # 如果帖子发布时间在1小时以内，显示几分钟之前
            minutes_ago = int(time_diff.total_seconds() / 60)
            return f"{minutes_ago}分钟前"
        elif time_diff < timedelta(days=1):
            # 如果帖子发布时间在1天以内，显示几小时之前
            hours_ago = int(time_diff.total_seconds() / 3600)
            return f"{hours_ago}小时前"
        else:
            # 否则，直接显示日期
            return postingTime.strftime('%Y年%m月%日 %时')


app = Flask(__name__, template_folder="templates", static_folder="static")
# SQL setup 之后需要再修改SQL地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Jbsd93233%@localhost/UserInfo'
sqlEngine = app.config['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
CORS(app)
app.secret_key = 'super secret key'


def getMostRecentPostID(modelName):
    with app.app_context():
        # 查询最后一条记录的ID
        last_id = modelName.query.order_by(modelName.threadNum.desc()).first()
        if last_id:
            next_id = last_id.threadNum + 1
        else:
            next_id = 1000  # 如果表为空，则从1开始
        return next_id
    
class user_register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    user_password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return '<user_register %r>' % self.username



# 建立posts相关的数据表
class teacher_posts(db.Model):
    posterId = db.Column(db.Integer)
    nickName = db.Column(db.String(80))
    title = db.Column(db.String(80), nullable=False)
    abstract = db.Column(db.String(80), nullable=False)
    threadNum = db.Column(db.Integer, nullable = False, primary_key=True, unique = True)
    teacherAbstract = db.Column(db.String(200), nullable = False)
    teacherRating = db.Column(db.Double, nullable=False)
    postingTime = db.Column(db.DateTime, nullable=False, default=translateTimetoBeijing(datetime.now(pytz.utc)))
    

    def __repr__(self):
        return '<teacher_posts %r>' % self.title
    
    def to_dict(self):
        post_dict = {
            'id': self.posterId,
            'nickname': self.nickName,
            'abstract': self.title,
            'threadNum': self.threadNum,
            'teacherAbstract': self.teacherAbstract,
            'rating': f"{self.teacherRating:.1f}",
            'postingTime': formatTimeStamp(self.postingTime)
        }

        post_dict['type'] = "teacher_posts"
        return post_dict
    

class student_posts(db.Model):
    posterId = db.Column(db.Integer)
    nickName = db.Column(db.String(80))
    title = db.Column(db.String(80), nullable=False)
    abstract = db.Column(db.String(80), nullable=False)
    threadNum = db.Column(db.Integer, nullable = False, primary_key=True, unique = True, autoincrement = True)
    isTeacher = db.Column(db.Boolean, nullable = False)
    postingTime = db.Column(db.DateTime, nullable=False, default=translateTimetoBeijing(datetime.now(pytz.utc)))


    def to_dict(self):
        post_dict = {
            'id': self.posterId,
            'nickname': self.nickName,
            'title': self.title,
            'abstract': self.abstract,
            'threadNum': self.threadNum,
            'isTeacher': self.isTeacher,
            'postingTime': formatTimeStamp(self.postingTime)
        }

        post_dict['type'] = "student_posts"
        return post_dict
    



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


@app.route("/", methods = ["GET", "POST"])
def index():
    new_user = None
    global verificaiton_getTime
    global verificationCode
    global verifPhone
    
    if request.method == "GET":
        return render_template('index.html')

    if request.method == "POST" :

        #注册逻辑--------------------------------------------------
        if request.headers.get('X-Action') == "signupVerification":
            userdata = request.get_json()
            
            new_user = user_register(
                fullname = userdata.get("fullname"),
                username = userdata.get("username"),
                user_password = userdata.get("password"),  # 这里应该是密码的哈希值，密码这边暂时保留
                phone = userdata.get("phoneNumber")
            )

            #判断数据库中是否已经被注册一些特定的信息
            user_exists = user_register.query.filter(user_register.username == new_user.username).first()
            phone_exists = user_register.query.filter(user_register.phone == new_user.phone).first()
            if(user_exists is not None):
                return jsonify({"error": "用户名已存在"})
            
            if(phone_exists is not None):
                return jsonify({"error": "电话号码已存在"})
            
            
            #发送验证码

            verificationCode=''.join([str(random.randint(0,9)) for _ in range(6)])

            #验证码flag开始检测
            session['verification_code'] = verificationCode
            print(f"Stored verification code: {session['verification_code']}")


            verificationParam = '{"code":' + '"' + str(verificationCode) + '"}'

            #时间戳，用于控制验证码有效期
            verificaiton_getTime = time.time()
            verifPhone = new_user.phone
            
            print(verificationParam)
            

            #验证码发送
            validation_code_json=userRegister.main("赵梓良的知予学习需求平台", "SMS_303861141", new_user.phone, verificationParam)

            #临时储存必要的动态验证码
            # if(os.path.exists(f'{new_user.phone}.txt')):
            #     open(f'{new_user.phone}.txt', 'w').close() #如果该临时文件存在，即再次获取验证码， 则清空该临时文件存储的验证码
            # with open(f'{new_user.phone}.txt', "w") as file:
            #     file.write(verificationCode)
            # file.close()
            return jsonify({"message": "验证码已发送"})

        #注册验证码逻辑
        elif(request.headers.get('X-Action') == "signupSubmit"):

            userInputVerifGroup = request.get_json()

            confirmedFullname = userInputVerifGroup.get("confirmedFullname")
            confirmedUsername = userInputVerifGroup.get("confirmedUserName")
            confirmedPassword = userInputVerifGroup.get("confirmedPassword")

            secondVerifPhone = userInputVerifGroup.get("phoneNumber")
            userInputVerif = userInputVerifGroup.get("verification")
            print("收回的信息：",verifPhone, userInputVerif)

  

            #检测是否已经获得验证码，或者验证码没有获取
            if(secondVerifPhone != verifPhone):
                return jsonify("与获得验证码的电话号码不匹配")
            
            elif(time.time() - verificaiton_getTime >= 120): #假设两分钟
                return jsonify("验证码已失效")
            # #读取验证码信息，确认用户输入的前后电话号码是否可以匹配上
            # with open(f'{verifPhone}.txt', "r") as f:
            #     desiredVerif = f.read()

            print("Test", userInputVerifGroup)
            
            if(userInputVerif == verificationCode):
                #os.remove(f'{verifPhone}.txt') #删除该文件节省内存
                new_user = user_register(
                    fullname = confirmedFullname,
                    username = confirmedUsername,
                    user_password = confirmedPassword,  # 这里应该是密码的哈希值，密码这边暂时保留
                    phone = verifPhone
                )
                db.session.add(new_user)
                
                try:
                    db.session.commit()
                    
                except Exception as e:
                    app.logger.error(f"Error adding new user: {e}")
                    db.session.rollback()
                    return jsonify({"error": "Error adding new user", "details": str(e)})

                verificationCode = ''
                verificaiton_getTime = ''
                verifPhone = 0
                return jsonify({"message": "注册成功"})
                
            else:
                return jsonify({"error": "验证码输入错误"})
            
        #登录逻辑-----------------------------------------------------------
        if request.headers.get('X-Action') == "loginVerification":
            loginPhoneInfo = request.get_json()
            loginPhoneNum = loginPhoneInfo.get("loginPhone")
            phone_exists = user_register.query.filter(user_register.phone == loginPhoneNum).first()

            if(phone_exists is None):
                return jsonify({"message": "用户未注册，请先注册"})
            
            else:
                verificationCode = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                # 验证码flag开始检测
                session['verification_code'] = verificationCode
                print(f"Stored verification code: {session['verification_code']}")

                verificationParam = '{"code":' + '"' + str(verificationCode) + '"}'
                validation_code_json=userRegister.main("赵梓良的知予学习需求平台", "SMS_303861141", verificationCode, verificationParam)
                
                #更新验证的电话号码和获得时间
                verifPhone = loginPhoneNum
                verificaiton_getTime = time.time()


            return jsonify({"message": "验证码已发送"})

        #验证验证码逻辑
        elif(request.headers.get('X-Action') == "loginSubmit"):
            userInputVerifGroup = request.get_json()
            secondverifPhone = userInputVerifGroup.get("loginPhone")
            userInputVerif = userInputVerifGroup.get("loginVerification")
            
            
            if(time.time() - verificaiton_getTime >= 120): #假设两分钟
                return jsonify("验证码已失效")

            if(secondverifPhone != verifPhone):
                return jsonify({"error" : "与获得验证码的电话号码不匹配"})
            
            # #读取验证码信息，确认用户输入的前后电话号码是否可以匹配上
            # with open(f'{verifPhone}.txt', "r") as f:
            #     desiredVerif = f.read()

            print("Test", userInputVerifGroup)
            if(userInputVerif == verificationCode):
                verificaiton_getTime = 0
                verificationCode = ''
                verifPhone = 0

                return jsonify({"message": "登录成功"})
            
                
            else:
                return jsonify({"error": "验证码输入错误"})
    return render_template('index.html')


def add_teacher_post(id, nickname, title, abstract, teacherAbstract, teacherRating):
    new_post = teacher_posts(posterId = id, nickName=nickname, title=title, abstract=abstract, threadNum=getMostRecentPostID(teacher_posts), teacherAbstract=teacherAbstract, teacherRating=teacherRating)
    db.session.add(new_post)
    db.session.commit()
    return new_post

def add_student_post(id, nickname, title, abstract, isTeacher):
    new_post = student_posts(posterId=id, nickName=nickname, title=title, abstract=abstract, threadNum=getMostRecentPostID(student_posts), isTeacher=isTeacher)
    db.session.add(new_post)
    db.session.commit()
    return new_post

@app.route("/search_results1", methods = ["GET", "POST"])
def TeacherSearchReturn():
    add_teacher_post(1001, "Richard", "Piano", "Welcome to this platform", "Level 10 Pianist", 4.24)
    add_teacher_post(1002, "Richard", "English", "Testing abstract", "Native English Speaker",3.00)
    add_teacher_post(1003, "Richard", "Spanish", "Teachers are welcome to register to this platform", "Graduated Spanish Master", 4.25)
    add_teacher_post(1004, "Richard", "Gaming", "Follow this guide to learn how to use this platform",  "Previous pro player", 4.88)
    add_teacher_post(1005, "Richard", "TikTok Management", "Looking for teachers for specific subjects", "100k followers on TikTok", 2.21)
    
    return render_template('teacher_posts.html')

@app.route("/search_results0", methods = ["GET", "POST"])
def StudetnSearchReturn():
    add_student_post(10001, "Richard", "Looking for an English teacher", "Has an score of....", False)
    add_student_post(2532,"Test2", "Willing to learn piano", "Currently I need...", False)
    add_student_post(654785, "Jery ", "Can someone help me with this?", "So far so good, but still need some support", False)
    add_student_post(3233, "Piasdf", "Need ergent help!", "URGENT!!!!", True)
    add_student_post(12121, "Qfkajf", "Welcome to student postings", "Welcome to our platform", False)
    
    return render_template('student_posts.html')


@app.route("/data")
def post_searchDisplay():
    type_param = request.args.get('type')
    if(type_param == "teacher_posts"):
        posts = teacher_posts.query.all()
        print(posts)
        return jsonify([p.to_dict() for p in posts])
    
    if(type_param == "student_posts"):
        posts = student_posts.query.all()
        print(posts)
        return jsonify([p.to_dict() for p in posts])
    return jsonify([]), 400 
#----------------------------



if __name__ == "__main__":
    app.run(debug = True)
