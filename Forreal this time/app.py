from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify # type: ignore
from functools import wraps
from flask_wtf.csrf import CSRFProtect # type: ignore
import secrets
from datetime import datetime
import re
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
import os
from app import create_app

app = create_app() 

import os
print("CWD:", os.getcwd())

if __name__ == '__main__':
    app.run(debug=True)
    