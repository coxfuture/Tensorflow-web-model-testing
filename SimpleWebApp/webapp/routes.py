from flask import render_template, Response, request, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image
import numpy as np

from webapp.camera import VideoCamera
from webapp.forms import RegistrationForm, LoginForm, CameraAddForm, UpdateAccountForm

from webapp.models import User, Camera
from webapp import app, db, bcrypt


@app.route('/')
@app.route('/home')
def home():
    cameras = Camera.query.all()
    return render_template('cameras.html', cameras=cameras)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

#camera feeds
def gen(camgen):
    while True:
        frame = camgen.get_frame()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')   

@app.route('/video_feed/<num>')       
def video_feed(num):
    w = Camera.query.get(num)
    fsrc = w.camera_link
    #because opencv usually needs a string, except when doing a webcam source
    if fsrc == '0':
        fsrc = 0
    
    profile = Camera.query.get(num).camera_profile
    print(profile)
    # if profile == 'gendetect':
    #     camclass = VideoCamera
    return Response(gen(VideoCamera(fsrc)), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/cameraConfig', methods=['GET','POST'])
def cameraConfig():
    form = CameraAddForm()
    if form.validate_on_submit():
        camera = Camera(camera_name=form.name.data,
                        camera_link=form.streamlink.data,camera_profile=form.profile.data)
        db.session.add(camera)
        db.session.commit()
        flash(f'Camera Added to DB','success')
    return render_template('camera-config.html',form=form)

@app.route('/updateCamera/<int:camera_id>', methods=['GET','POST'])
def updateCamera(camera_id):
    camera = Camera.query.get_or_404(camera_id)
    form = CameraAddForm()
    if form.validate_on_submit():        
        camera.camera_name = form.name.data
        camera.camera_link = form.streamlink.data
        db.session.commit()
        flash(f'Camera Updated in Database','success')
    elif request.method == 'GET':
        form.name.data = camera.camera_name
        form.streamlink.data = camera.camera_link
    return render_template('updatecamera.html', form=form, camera_id=camera.id, camera=camera)

@app.route("/updateCamera/<int:camera_id>/delete", methods=['POST'])
@login_required
def delete_camera(camera_id):
    camera = Camera.query.get_or_404(camera_id)
    db.session.delete(camera)
    db.session.commit()
    flash('Camera Removed', 'success')
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account has been created!','success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f'Your Account has been updated!','success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.username.data = current_user.username  
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', form=form, image_file=image_file)



