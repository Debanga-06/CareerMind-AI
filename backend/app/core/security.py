"""
Password hashing + JWT issuance/verification + FastAPI auth dependencies.

Password hashing uses passlib's pbkdf2_sha256 scheme rather than bcrypt.
This is a deliberate choice for this project: pbkdf2_sha256 is a
pure-Python-compatible, well-vetted algorithm with no native-extension
version-compatibility issues, which keeps the MVP easy to install
anywhere. Swapping to bcrypt/argon2 later is a one-line change to
`pwd_context` below and does not affect any calling code.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

settings = get_settings()

# tokenUrl is only used to populate Swagger UI's "Authorize" flow; the
# actual login endpoint accepts JSON (see schemas/auth.py + api/auth.py).
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=True)
_oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=False
)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    settings_ = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings_.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings_.JWT_SECRET_KEY, algorithm=settings_.JWT_ALGORITHM)


def _decode_token_subject(token: str) -> Optional[str]:
    settings_ = get_settings()
    try:
        payload = jwt.decode(token, settings_.JWT_SECRET_KEY, algorithms=[settings_.JWT_ALGORITHM])
    except JWTError:
        return None
    return payload.get("sub")


_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str = Depends(_oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Required auth: raises 401 if the token is missing/invalid or the user no longer exists."""
    user_id = _decode_token_subject(token)
    if user_id is None:
        raise _CREDENTIALS_ERROR

    user = db.get(User, int(user_id))
    if user is None:
        raise _CREDENTIALS_ERROR
    return user


def get_current_user_optional(
    token: Optional[str] = Depends(_oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Optional auth: returns None (never raises) if there's no/invalid token."""
    if not token:
        return None
    user_id = _decode_token_subject(token)
    if user_id is None:
        return None
    return db.get(User, int(user_id))
