from flask import Blueprint
from flask import Flask, render_template, request, jsonify, json, session
from models import user_register, db
import random
from sms_verification import userRegister
from users import userInfo
import time


indexpage = Blueprint('indexpage', __name__)

verificaiton_getTime = 0
verificationCode = ''
verifPhone = 0

@indexpage.route("/", methods=["GET", "POST"])
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