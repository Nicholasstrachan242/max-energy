import pyotp
import qrcode
import io
import base64
from PIL import Image
from datetime import datetime
from flask import Blueprint, send_file, session, redirect, url_for, request, flash, render_template
from db import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('Please enter both username and password')
            return render_template('login.html')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if user.is_2fa_enabled:
                session['pending_2fa_user'] = user.username
                return redirect(url_for('auth.twofa_verify'))
            session['username'] = username
            session['role'] = user.role.name
            user.last_login = datetime.utcnow()
            db.session.commit()
            if user.role.name == 'admin':
                return redirect(url_for('admin.role_management'))
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    # Your logout logic here
    session.clear()
    return redirect(url_for('auth.login'))  # or wherever you want to redirect

@auth_bp.route('/2fa-setup', methods=['GET', 'POST'])
def twofa_setup():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('User not found.')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        otp = request.form.get('otp')
        if pyotp.TOTP(user.totp_secret).verify(otp):
            user.is_2fa_enabled = True
            db.session.commit()
            flash('2FA enabled! Please use your authenticator app to log in.')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid OTP code. Please try again.')

    if not user.totp_secret:
        user.totp_secret = pyotp.random_base32()
        db.session.commit()
    totp_uri = pyotp.totp.TOTP(user.totp_secret).provisioning_uri(
        name=user.username, issuer_name="Maxx Energy"
    )

    # Generate QR code with logo
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Add logo to QR code
    logo_path = 'static/images/BW maxx energy logo.png'  # Adjust path if needed
    try:
        logo = Image.open(logo_path)
        box_size = min(img.size) // 4
        logo = logo.resize((box_size, box_size))
        pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
        img.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)
    except Exception as e:
        print("Logo not found or error adding logo:", e)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    qr_b64 = "data:image/png;base64," + base64.b64encode(buf.read()).decode('utf-8')
    return render_template('2fa_setup.html', qr_code=qr_b64, secret=user.totp_secret)

@auth_bp.route('/2fa-verify', methods=['GET', 'POST'])
def twofa_verify():
    username = session.get('pending_2fa_user')
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found.')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        otp = request.form.get('otp')
        if pyotp.TOTP(user.totp_secret).verify(otp,  valid_window=1):
            session['username'] = user.username
            session['role'] = user.role.name
            user.last_login = datetime.utcnow()
            db.session.commit()
            session.pop('pending_2fa_user', None)
            if user.role.name == 'admin':
                return redirect(url_for('admin.role_management'))
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid OTP code')
    return render_template('2fa_verify.html') 