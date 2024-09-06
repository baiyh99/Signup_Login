from flask import Flask, render_template, request, flash, jsonify, json, session
from flask.views import MethodView
from extension import db, cors
from flask_cors import CORS
from users import userInfo
import os, random
from sms_verification import userRegister

app = Flask(__name__, template_folder="templates", static_folder="static")
# SQL setup 之后需要再修改SQL地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Jbsd93233%@localhost/UserInfo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
CORS(app)
app.secret_key = 'super secret key'



class user_register(db.Model):
    #id = db.Column()
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    user_password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return '<user_register %r>' % self.username


# shell里输入flask recreate重置用户注册信息数据表
@app.cli.command('recreate')
def create():
    db.drop_all()
    db.create_all()

@app.route("/", methods = ["GET", "POST"])
def index():
    new_user = None
    
    if request.method == "GET":
        return render_template('index.html')

    if request.method == "POST" :

        #注册逻辑--------------------------------------------------
        if request.headers.get('X-Action') == "signupVerification":
            userdata = request.get_json()
            
            new_user = user_register(
                fullname = userdata.get("fullname"),
                username = userdata.get("username"),
                user_password = userdata.get("password"),  # 在实际应用中，这里应该是密码的哈希值
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
            verficationCode=''.join([str(random.randint(0,9)) for _ in range(6)])
            
            #验证码flag开始检测
            session['verification_code'] = verficationCode
            print(f"Stored verification code: {session['verification_code']}")
            
            verificationParam = '{"code":' + '"' + str(verficationCode) + '"}'
            print(verificationParam)
            

            #验证码发送
            validation_code_json=userRegister.main("赵梓良的知予学习需求平台", "SMS_303861141", new_user.phone, verificationParam)

            #临时储存必要的动态验证码

            if(os.path.exists(f'{new_user.phone}.txt')):
                open(f'{new_user.phone}.txt', 'w').close() #如果该临时文件存在，即再次获取验证码， 则清空该临时文件存储的验证码
            with open(f'{new_user.phone}.txt', "w") as file:
                file.write(verficationCode)
            file.close()

            

            return jsonify({"message": "验证码已发送"})
        

        #注册验证码逻辑
        elif(request.headers.get('X-Action') == "signupSubmit"):

            userInputVerifGroup = request.get_json()
            
            verifPhone = userInputVerifGroup.get("phoneNumber")
            userInputVerif = userInputVerifGroup.get("verification")
            print(verifPhone, userInputVerif)
            if(not os.path.exists(verifPhone)):
                return jsonify("与获得验证码的电话号码不匹配")
            
            #读取验证码信息，确认用户输入的前后电话号码是否可以匹配上
            with open(f'{verifPhone}.txt', "r") as f:
                desiredVerif = f.read()
            file.close()
            
            desiredVerif.strip()
            print("Test", userInputVerifGroup)
            if(userInputVerif == desiredVerif):

                os.remove(f'{verifPhone}.txt') #删除该文件节省内存
                db.session.add(new_user)
                
                try:
                    db.session.commit()


                    
                except Exception as e:
                    app.logger.error(f"Error adding new user: {e}")
                    db.session.rollback()
                    return jsonify({"error": "Error adding new user", "details": str(e)})
                
                return jsonify({"message": "注册成功"})
                
            else:
                return jsonify({"error": "验证码输入错误"})
            
        #登录逻辑-----------------------------------------------------------
        if request.headers.get('X-Action') == "loginVerification":
            userPhone = request.get_json()
            phone_exists = user_register.query.filter(user_register.phone == new_user.phone).first()

            if(phone_exists is None):
                return jsonify({"message": "用户未注册，请先注册"})
            
            else:
                validation_code_json=userRegister.main("赵梓良的知予学习需求平台", "SMS_303861141", new_user.phone, verificationParam)
                
                #临时文件
                if(os.path.exists(f'{new_user.phone}.txt')):
                    open(f'{new_user.phone}.txt', 'w').close() #如果该临时文件存在，即再次获取验证码， 则清空该临时文件存储的验证码
                with open(f'{new_user.phone}.txt', "w") as file:
                    file.write(verficationCode)
                file.close()

            return jsonify({"message": "验证码已发送"})

        #注册验证码逻辑
        elif(request.headers.get('X-Action') == "LoginSubmit"):
            userInputVerifGroup = request.get_json()
            verifPhone = userInputVerifGroup.get("phoneNumber")
            userInputVerif = userInputVerifGroup.get("verification")
            print(verifPhone, userInputVerif)
            if(not os.path.exists(verifPhone)):
                return jsonify("与获得验证码的电话号码不匹配")
            
            #读取验证码信息，确认用户输入的前后电话号码是否可以匹配上
            with open(f'{verifPhone}.txt', "r") as f:
                desiredVerif = f.read()
            file.close()
            
            desiredVerif.strip()
            print("Test", userInputVerifGroup)
            if(userInputVerif == desiredVerif):

                os.remove(f'{verifPhone}.txt') #删除该文件节省内存
                db.session.add(new_user)
                
                try:
                    db.session.commit()


                    
                except Exception as e:
                    app.logger.error(f"Error adding new user: {e}")
                    db.session.rollback()
                    return jsonify({"error": "Error adding new user", "details": str(e)})
                
                return jsonify({"message": "注册成功"})
                
            else:
                return jsonify({"error": "验证码输入错误"})
    return render_template('index.html')
    

#----------------------------
if __name__ == "__main__":
    app.run(debug = True)
