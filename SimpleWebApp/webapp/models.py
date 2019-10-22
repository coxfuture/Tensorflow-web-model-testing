from datetime import datetime
from webapp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_name = db.Column(db.String(20), nullable=False)
    camera_link = db.Column(db.String(240), nullable=False)
    camera_profile = db.Column(db.String(40))
    
    def __repr__(self):
        return f"Camera('{self.camera_name}', '{self.camera_link}','{self.camera_profile}')"

# class Alert(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     alert_type = db.Column(db.String(120), nullable=False)
#     alert_severity = db.Column(db.String(240) nullable=False)
#     alert_time = db.Column(db.String(120), nullable=False)
    
#     def __repr__(self):
#         return f"Camera('{self.alert_type}', '{self.alert_severity}', '{self.alert_time}')"