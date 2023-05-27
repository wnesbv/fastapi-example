
from datetime import datetime, timedelta

import jwt

from fastapi import HTTPException, status
from passlib.context import CryptContext

from config.settings import settings


class Auth:
    hasher = CryptContext(schemes=["bcrypt"])
    secret = settings.SECRET_KEY

    def hash_password(self, password):
        return self.hasher.hash(password)

    def verify_password(self, password, encoded_password):
        return self.hasher.verify(password, encoded_password)


    def encode_token(self, username, user):

        payload = {
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "scope": "access_token",
            "sub": username,
        }
        return jwt.encode(payload, self.secret, algorithm=settings.ALGORITHM)


    def decode_token(self, token):
        payload = jwt.decode(token, self.secret, algorithms=[settings.ALGORITHM])
        if payload["scope"] == "access_token":
            return payload["sub"]


    # ...


    def encode_verification_token(self, username):
        payload = {
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.EMAIL_TOKEN_EXPIRY_MINUTES),
            "iat": datetime.utcnow(),
            "scope": "email_verification",
            "sub": username,
        }
        return jwt.encode(payload, self.secret, algorithm=settings.ALGORITHM)


    def verify_email(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[settings.ALGORITHM])

            if payload["scope"] == "email_verification":
                username = payload["sub"]
                return username
            raise HTTPException(status_code=401, detail="Invalid scope for token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Email token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid email token")


    def encode_reset_token(self, username):
        payload = {
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.RESET_TOKEN_EXPIRY_MINUTES),
            "iat": datetime.utcnow(),
            "scope": "reset_token",
            "sub": username,
        }
        return jwt.encode(payload, self.secret, algorithm=settings.ALGORITHM)


    def verify_reset_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[settings.ALGORITHM])

            if payload["scope"] == "reset_token":
                username = payload["sub"]
                return username
            raise HTTPException(status_code=401, detail="Invalid scope for token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Reset token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid reset token")


auth = Auth()
