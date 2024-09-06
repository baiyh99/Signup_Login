# from flask import Flask, request, redirect, render_template, flash, url_for
#
# @app.before_request
# def create_tables():
#     db.create_all()
#
#
# #First page
# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"
#
#
# #Registration page
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         retype_pswd = request.form["retype_pswd"]
#
#         if(password != retype_pswd):
#             flash("两次密码输入不匹配，请再试一次")
#             return render_template('register.html')
#
#         #Check username uniqueness
#         if userInfo.query.filter_by(username=username).first():
#             flash("用户名已存在，请重新输入用户名")
#             return render_template('register.html')
#
#         new_user = userInfo(username=username)
#         new_user.set_password(password)
#
#         db.session.add(new_user)
#         db.session.commit()
#
#         flash("User registered successfully!")
#         return redirect(url_for("hello_world"))
#
#     return render_template("register.html")
#
#
#
# if __name__ == '__main__':
#     app.run(debug = True)