
from fastapi import BackgroundTasks, HTTPException, Request

from sqlalchemy.orm import Session

from config.settings import settings
from config.mail import send_mail
from account.auth import auth
from .views import get_user_by_email
from . import schemas





