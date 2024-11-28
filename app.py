from flask import Flask, render_template, request, flash, jsonify, json
from flask.views import MethodView
from extension import db, cors
from flask_cors import CORS
from users import userInfo
import os

app = Flask(__name__, template_folder="templates", static_folder="static")
# SQL setup 之后需要再修改SQL地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Jbsd93233%@localhost/UserInfo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
CORS(app)
app.secret_key = 'super secret key'

@app.cli.command()
def create():
    db.drop_all()
    db.create_all()

class user_register(db.Model):
    #id = db.Column()
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    user_password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return '<user_register %r>' % self.username


@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template('index.html')
    else:
        userdata = request.get_json()
        fullname = userdata.get("fullname")
        username = userdata.get("username")
        password = userdata.get("password")
        retypepassword = userdata.get("retypepassword")
        
        print(fullname, username, password, retypepassword)
        
        new_user = user_register(
            fullname = userdata.get("fullname"),
            username = userdata.get("username"),
            user_password = userdata.get("password"),  # 在实际应用中，这里应该是密码的哈希值
            phone = userdata.get("phoneNumber")
            
        )
        db.session.add(new_user)
        
        try:
            db.session.commit()
            return jsonify({"message": "User registered successfully"})
            
        except Exception as e:
            app.logger.error(f"Error adding new user: {e}")
            db.session.rollback()
            return jsonify({"error": "Error adding new user", "details": str(e)})
            
        if(password != retypepassword):
            return jsonify({"error": "FLASK Passwords do not match"})


        return render_template('index.html')
    



# class userSignup_Login(MethodView):
#     def get(self): #注册界面
#         return render_template()
#     def post(self): #
#         return "Post"

# register = userSignup_Login.as_view('register')
# app.add_url_rule('/register/', view_func = register, methods = ['GET',])

#----------------------------
if __name__ == "__main__":
    app.run(debug = True)
