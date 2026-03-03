from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


def _authenticate_user(email: str, password: str, db: Session) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"message": "Invalid credentials"})

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"message": "Inactive user"})

    return user


@router.post("/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> Token:
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": "Email already exists"})

    organization = db.query(Organization).filter(Organization.name == payload.organization_name).first()
    if organization is None:
        organization = Organization(name=payload.organization_name)
        db.add(organization)
        db.flush()

    existing_org_user_count = db.query(User).filter(User.organization_id == organization.id).count()
    assigned_role = UserRole.ADMIN if existing_org_user_count == 0 else UserRole.RESEARCHER

    user = User(
        email=payload.email,
        hashed_password="",
        full_name=payload.full_name,
        role=assigned_role,
        organization_id=organization.id,
        is_active=True,
    )
    try:
        user.hashed_password = get_password_hash(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": str(exc)})
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id)
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = _authenticate_user(payload.email, payload.password, db)
    token = create_access_token(subject=user.id)
    return Token(access_token=token)
