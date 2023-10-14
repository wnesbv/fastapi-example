
from datetime import datetime, timedelta

import jwt, bcrypt

from fastapi import HTTPException, status

from config.settings import settings


class Auth:
    secret = settings.SECRET_KEY

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed

    async def verify_password(self, password, encoded_password):
        verify = bcrypt.checkpw(password.encode(), encoded_password)
        return verify


    async def encode_token(self, username, user):

        payload = {
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "scope": "access_token",
            "sub": username,
        }
        return jwt.encode(
            payload, self.secret, algorithm=settings.ALGORITHM
        )


    async def decode_token(self, token):

        payload = jwt.decode(
            token, self.secret, algorithms=settings.ALGORITHM
        )
        if payload["scope"] == "access_token":
            return payload["sub"]
        return False


    async def decode_token_all(self, token):

        payload = jwt.decode(
            token, self.secret, algorithms=settings.ALGORITHM
        )
        if payload["scope"] == "access_token":
            return payload
        return False


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
            payload = jwt.decode(
                token, self.secret, algorithms=settings.ALGORITHM
            )

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


    async def verify_reset_token(self, token):
        try:
            payload = jwt.decode(
                token, self.secret, algorithms=settings.ALGORITHM
            )

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
