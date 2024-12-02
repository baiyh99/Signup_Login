from flask import Blueprint
from flask import Flask, render_template, request, jsonify, json, session
from models import teacher_posts, db, translateTimetoBeijing, formatTimeStamp
import pytz
from datetime import datetime, timedelta, timezone


teacher_postings = Blueprint('search_results1', __name__)

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
        
def getMostRecentPostID():
    last_id = teacher_posts.query.order_by(teacher_posts.threadNum.desc()).first()
    if last_id:
        return last_id.threadNum + 1
    else:
        return 1000  # 如果表为空，则从1开始
    

def add_teacher_post(id, nickname, title, abstract, teacherAbstract, teacherRating):
    new_post = teacher_posts(posterId = id, nickName=nickname, title=title, abstract=abstract, threadNum=getMostRecentPostID(), teacherAbstract=teacherAbstract, teacherRating=teacherRating)
    db.session.add(new_post)
    db.session.commit()
    return new_post


@teacher_postings.route("/", methods = ["GET", "POST"])
def TeacherSearchReturn():
    add_teacher_post(1001, "Richard", "Piano", "Welcome to this platform", "Level 10 Pianist", 4.24)
    add_teacher_post(1002, "Richard", "English", "Testing abstract", "Native English Speaker",3.00)
    add_teacher_post(1003, "Richard", "Spanish", "Teachers are welcome to register to this platform", "Graduated Spanish Master", 4.25)
    add_teacher_post(1004, "Richard", "Gaming", "Follow this guide to learn how to use this platform",  "Previous pro player", 4.88)
    add_teacher_post(1005, "Richard", "TikTok Management", "Looking for teachers for specific subjects", "100k followers on TikTok", 2.21)
    
    return render_template('teacher_posts.html')

@teacher_postings.route("/data")
def post_searchDisplay():
    type_param = request.args.get('type')
    if(type_param == "teacher_posts"):
        posts = teacher_posts.query.all()
        print(posts)
        return jsonify([p.to_dict() for p in posts])
    
    # if(type_param == "student_posts"):
    #     posts = student_posts.query.all()
    #     print(posts)
    #     return jsonify([p.to_dict() for p in posts])
    return jsonify([]), 400 