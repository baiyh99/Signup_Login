from flask_sqlalchemy import SQLAlchemy
import pytz
from datetime import datetime, timedelta
from extension import db
# db = SQLAlchemy()


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
        
def translateTimetoBeijing(utc_time):
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_time = utc_time.astimezone(beijing_tz)
    return beijing_time.replace(tzinfo=None)


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