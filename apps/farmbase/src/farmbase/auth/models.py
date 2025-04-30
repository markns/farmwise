from __future__ import annotations

import secrets
import string
from datetime import UTC, datetime, timedelta
from typing import List, Optional
from uuid import uuid4

import bcrypt
from jose import jwt
from pydantic import Field, validator
from pydantic.networks import EmailStr
from sqlalchemy import Boolean, Column, Integer, LargeBinary, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy_utils import TSVectorType

from farmbase.config import (
    FARMBASE_JWT_ALG,
    FARMBASE_JWT_EXP,
    FARMBASE_JWT_SECRET,
)
from farmbase.database.core import Base
from farmbase.enums import FarmbaseEnum, UserRoles
from farmbase.models import FarmbaseBase, OrganizationSlug, Pagination, PrimaryKey, TimeStampMixin
from farmbase.organization.models import Organization, OrganizationRead
from farmbase.project.models import Project, ProjectRead


def generate_password():
    """Generates a reasonable password if none is provided."""
    alphanumeric = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphanumeric) for i in range(10))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)  # noqa
            and sum(c.isdigit() for c in password) >= 3  # noqa
        ):
            break
    return password


def hash_password(password: str):
    """Generates a hashed version of the provided password."""
    pw = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)


class FarmbaseUser(Base, TimeStampMixin):
    __table_args__ = {"schema": "farmbase_core"}

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    last_mfa_time: Mapped[datetime] = mapped_column(nullable=True)
    experimental_features: Mapped[bool] = mapped_column(default=False)

    # relationships
    # events = relationship("Event", backref="farmbase_user")
    projects: Mapped[List[FarmbaseUserProject]] = relationship(
        back_populates="farmbase_user",
        cascade="all, delete-orphan",
    )

    # TODO: look into https://docs.sqlalchemy.org/en/20/orm/extensions/associationproxy.html#simplifying-association-objects
    # This conflicts with the projects in FarmbaseBase
    # projects: AssociationProxy[List[Project]] = association_proxy(
    #     "projects",
    #     "project",
    #     creator=lambda project_obj: FarmbaseUserProject(project=project_obj),
    # )

    organizations: Mapped[List[FarmbaseUserOrganization]] = relationship(back_populates="farmbase_user")

    search_vector = Column(TSVectorType("email", regconfig="pg_catalog.simple", weights={"email": "A"}))

    def verify_password(self, password: str) -> bool:
        """Verify if provided password matches stored hash"""
        if not password or not self.password:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    def set_password(self, password: str) -> None:
        """Set a new password"""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password = hash_password(password)

    def is_owner(self, organization_slug: str) -> bool:
        """Check if user is an owner in the given organization"""
        role = self.get_organization_role(organization_slug)
        return role == UserRoles.owner

    @property
    def token(self):
        now = datetime.now(UTC)
        exp = (now + timedelta(seconds=FARMBASE_JWT_EXP)).timestamp()
        data = {
            "exp": exp,
            "email": self.email,
        }
        return jwt.encode(data, FARMBASE_JWT_SECRET, algorithm=FARMBASE_JWT_ALG)

    async def get_organization_role(self, organization_slug: OrganizationSlug):
        """Gets the user's role for a given organization slug."""
        for o in self.organizations:
            if o.organization.slug == organization_slug:
                return o.role
        return None


# TODO use mapped_column as here: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#association-object
class FarmbaseUserProject(Base, TimeStampMixin):
    farmbase_user_id: Mapped[int] = mapped_column(ForeignKey(FarmbaseUser.id), primary_key=True)
    farmbase_user: Mapped[FarmbaseUser] = relationship(back_populates="projects")

    project_id: Mapped[int] = mapped_column(ForeignKey(Project.id), primary_key=True)
    project: Mapped[Project] = relationship(back_populates="user_assoc")

    default = Column(Boolean, default=False)

    role = Column(String, nullable=False, default=UserRoles.member)


class FarmbaseUserOrganization(Base, TimeStampMixin):
    __table_args__ = {"schema": "farmbase_core"}
    farmbase_user_id: Mapped[int] = mapped_column(ForeignKey(FarmbaseUser.id), primary_key=True)
    farmbase_user: Mapped[FarmbaseUser] = relationship(back_populates="organizations")

    organization_id: Mapped[int] = mapped_column(ForeignKey(Organization.id), primary_key=True)
    organization: Mapped[Organization] = relationship(back_populates="users")

    role = Column(String, default=UserRoles.member)


# -- Pydantic


class UserProject(FarmbaseBase):
    project: ProjectRead
    default: Optional[bool] = False
    role: Optional[str] = Field(None, nullable=True)


class UserOrganization(FarmbaseBase):
    organization: OrganizationRead
    default: Optional[bool] = False
    role: Optional[str] = Field(None, nullable=True)


class UserBase(FarmbaseBase):
    email: EmailStr
    projects: Optional[List[UserProject]] = []
    organizations: Optional[List[UserOrganization]] = []

    @validator("email")
    def email_required(cls, v):
        if not v:
            raise ValueError("Must not be empty string and must be a email")
        return v


class UserLogin(UserBase):
    password: str

    @validator("password")
    def password_required(cls, v):
        if not v:
            raise ValueError("Must not be empty string")
        return v


class UserRegister(UserLogin):
    password: Optional[str] = Field(None, nullable=True)

    @validator("password", pre=True, always=True)
    def password_required(cls, v):
        # we generate a password for those that don't have one
        password = v or generate_password()
        return hash_password(password)


class UserLoginResponse(FarmbaseBase):
    projects: Optional[List[UserProject]]
    token: Optional[str] = Field(None, nullable=True)


class UserRead(UserBase):
    id: PrimaryKey
    role: Optional[str] = Field(None, nullable=True)
    # experimental_features: Optional[bool]


class UserUpdate(FarmbaseBase):
    id: PrimaryKey
    projects: Optional[List[UserProject]]
    organizations: Optional[List[UserOrganization]]
    # experimental_features: Optional[bool]
    role: Optional[str] = Field(None, nullable=True)


class UserPasswordUpdate(FarmbaseBase):
    """Model for password updates only"""

    current_password: str
    new_password: str

    @validator("new_password")
    def validate_password(cls, v):
        if not v or len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        # Check for at least one number
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        # Check for at least one uppercase and one lowercase character
        if not (any(c.isupper() for c in v) and any(c.islower() for c in v)):
            raise ValueError("Password must contain both uppercase and lowercase characters")
        return v

    @validator("current_password")
    def password_required(cls, v):
        if not v:
            raise ValueError("Current password is required")
        return v


class AdminPasswordReset(FarmbaseBase):
    """Model for admin password resets"""

    new_password: str

    @validator("new_password")
    def validate_password(cls, v):
        if not v or len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        # Check for at least one number
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        # Check for at least one uppercase and one lowercase character
        if not (any(c.isupper() for c in v) and any(c.islower() for c in v)):
            raise ValueError("Password must contain both uppercase and lowercase characters")
        return v


class UserCreate(FarmbaseBase):
    email: EmailStr
    password: Optional[str] = Field(None, nullable=True)
    projects: Optional[List[UserProject]]
    organizations: Optional[List[UserOrganization]]
    role: Optional[str] = Field(None, nullable=True)

    @validator("password", pre=True)
    def hash(cls, v):
        return hash_password(str(v))


class UserRegisterResponse(FarmbaseBase):
    token: Optional[str] = Field(None, nullable=True)


class UserPagination(Pagination):
    items: List[UserRead] = []


class MfaChallengeStatus(FarmbaseEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class MfaChallenge(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    valid = Column(Boolean, default=False)
    reason = Column(String, nullable=True)
    action = Column(String)
    status = Column(String, default=MfaChallengeStatus.PENDING)
    challenge_id = Column(UUID(as_uuid=True), default=uuid4, unique=True)
    farmbase_user_id: Mapped[int] = mapped_column(ForeignKey(FarmbaseUser.id), nullable=False)
    farmbase_user = relationship(FarmbaseUser, backref="mfa_challenges")


class MfaPayloadResponse(FarmbaseBase):
    status: str


class MfaPayload(FarmbaseBase):
    action: str
    project_id: int
    challenge_id: str
