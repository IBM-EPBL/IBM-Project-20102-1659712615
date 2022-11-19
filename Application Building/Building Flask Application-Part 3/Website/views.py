from flask import Blueprint, render_template, Response, request, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .auth import webcam_release

views = Blueprint('views', __name__)


@views.route('/',methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        webcam_release()
        logout_user()
        return redirect(url_for('auth.login'))
    return render_template('home.html', user=current_user)

