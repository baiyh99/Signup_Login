# 导入Flask模块和SQLAlchemy
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# 实例化Flask应用
app = Flask(__name__)

# 数据库配置，替换以下参数为你的MySQL数据库信息
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化SQLAlchemy
db = SQLAlchemy(app)


# 定义用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


# 创建数据库表
@app.before_first_request
def create_tables():
    db.create_all()


# 首页路由
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# 注册路由
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 获取表单数据
        username = request.form["username"]
        password = request.form["password"]

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("register"))

        # 创建新用户实例并设置密码
        new_user = User(username=username)
        new_user.set_password(password)

        # 添加到数据库会话并提交
        db.session.add(new_user)
        db.session.commit()

        # 闪送成功消息
        flash("User registered successfully!")
        return redirect(url_for("hello_world"))

    # GET请求，渲染注册表单
    return render_template("register.html")


# 运行Flask应用
if __name__ == "__main__":
    app.run(debug=True)