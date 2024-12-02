from flask import Blueprint
from flask import Flask, render_template, request, jsonify, json, session
from models import student_posts, db, formatTimeStamp
import pytz
from datetime import datetime, timedelta, timezone
from assistMethods import add_student_post


student_postings = Blueprint('search_results0', __name__)


        


@student_postings.route("/", methods = ["GET", "POST"])
def StudetnSearchReturn():
    # add_student_post(10001, "Richard", "Looking for an English teacher", "Has an score of....", False)
    # add_student_post(2532,"Test2", "Willing to learn piano", "Currently I need...", False)
    # add_student_post(654785, "Jery ", "Can someone help me with this?", "So far so good, but still need some support", False)
    # add_student_post(3233, "Piasdf", "Need ergent help!", "URGENT!!!!", True)
    # add_student_post(12121, "Qfkajf", "Welcome to student postings", "Welcome to our platform", False)
    
    return render_template('student_posts.html')

@student_postings.route("/data")
def post_searchDisplay():
    type_param = request.args.get('type')
    if(type_param == "student_posts"):
        posts = student_posts.query.all()
        print(posts)
        return jsonify([p.to_dict() for p in posts])
    
    # if(type_param == "student_posts"):
    #     posts = student_posts.query.all()
    #     print(posts)
    #     return jsonify([p.to_dict() for p in posts])
    return jsonify([]), 400 