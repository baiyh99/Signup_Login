from models import db, user_register, teacher_posts, student_posts

logged_in_phone = 0


def getUserInfo(phoneNum):
    if(phoneNum == 0):
        return 0

    else:
        userInfo = user_register.query.filter(user_register.phone == phoneNum).first()

        if userInfo:
            username = userInfo.username
            id = userInfo.id
            fullname = userInfo.fullname

            return[id, username, fullname]
        
def add_teacher_post(id, nickname, title, abstract, teacherAbstract, teacherRating):
    new_post = teacher_posts(posterId = id, nickName=nickname, title=title, abstract=abstract, threadNum=getMostRecentPostID_teacher(), teacherAbstract=teacherAbstract, teacherRating=teacherRating)
    db.session.add(new_post)
    db.session.commit()
    return new_post


def add_student_post(id, nickname, title, abstract, isTeacher):
    new_post = student_posts(posterId=id, nickName=nickname, title=title, abstract=abstract, threadNum=getMostRecentPostID_student(), isTeacher=isTeacher)
    db.session.add(new_post)
    db.session.commit()
    return new_post

def getMostRecentPostID_teacher():
    last_id = teacher_posts.query.order_by(teacher_posts.threadNum.desc()).first()
    if last_id:
        return last_id.threadNum + 1
    else:
        return 1000  # 如果表为空，则从1开始
    
def getMostRecentPostID_student():
    last_id = student_posts.query.order_by(student_posts.threadNum.desc()).first()
    if last_id:
        return last_id.threadNum + 1
    else:
        return 1000  # 如果表为空，则从1开始