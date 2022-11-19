from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import cv2



model = load_model('trained_model.h5')
video = cv2.VideoCapture(0)
index = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']

auth = Blueprint('auth', __name__)


def get_frames():
    while 1:
        success, frame = video.read()
        if not success:
            break
        else:
            cv2.imwrite('image.jpg', frame)
            img = image.load_img('image.jpg', target_size=(64, 64))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            prediction = np.argmax(model.predict(x), axis=1)
            y = prediction[0]
            cv2.rectangle(frame, (0, 0), (640,480), (0,0,0), 5)
            cv2.putText(frame,'Prediction : '+str(index[y]),(100,100),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),4)
            cv2.imwrite("image.jpg",frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
def webcam_release():
    video.release()
    cv2.destroyAllWindows()
    return


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('User does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout',methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('User already exists.', category='error')
        elif len(email) < 4 or (not('@' in email)):
            flash('Invalid Email ID. Email must be greater than 3 characters and should contain \'@\'.', category='error')
        elif len(first_name) < 2:
            flash('First Name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name,
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created successfully!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/video_feed')
def video_feed():
    return Response(get_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@auth.route('/stop')
def stop():
    webcam_release()
    return redirect(url_for('auth.logout'))