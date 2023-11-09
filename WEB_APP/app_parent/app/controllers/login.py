from functools import wraps
from flask import session
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'logged_in' not in session or session['logged_in']==False:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function