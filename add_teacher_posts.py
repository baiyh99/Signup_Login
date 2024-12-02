from flask import Blueprint, render_template

template_path = 'templates/add_teacher_posts.html'
add_teacher_posts = Blueprint('add_posts1', __name__)


@add_teacher_posts.route("/", methods = ["GET", "POST"])
def addPosts():
    return render_template('add_teacher_posts.html')