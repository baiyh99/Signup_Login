from flask import Blueprint, render_template, request, jsonify
from assistMethods import logged_in_phone
from flask_cors import CORS
from assistMethods import add_student_post, getUserInfo


template_path = 'templates/add_student_posts.html'
add_student_posts = Blueprint('add_post0', __name__)
CORS(add_student_posts)

@add_student_posts.route("/", methods = ["GET"])
def addPosts():
    return render_template('add_student_posts.html')


@add_student_posts.route("/data", methods = ["POST"])
def addToDataSet():
    if request.method == "POST":
        postInfo = request.get_json()
        if postInfo:
            print(postInfo)
        else:
            print("No JSON data received")

    print("Current Login Status: ", logged_in_phone)
    if(logged_in_phone == 0):
        return jsonify({"error": "请先登录才可发帖"})
    else:
        [userID, username, fullname] = getUserInfo(logged_in_phone)
        add_student_post(userID, fullname, postInfo.get("title"), postInfo.get("abstract"), False)#rating needs to be updated later
        return jsonify({"message": "帖子发布成功"})