import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, 
    Integer, Text, JSON, Enum as SQLEnum, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class UserRole(str, Enum):
    ADMIN = "admin"
    CAPTAIN = "captain"
    MEMBER = "member"

class ChallengeCategory(str, Enum):
    WEB = "web"
    CRYPTO = "crypto"
    FORENSICS = "forensics"
    PWN = "pwn"
    REV = "rev"
    MISC = "misc"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    INSANE = "insane"

class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"

class CheckType(str, Enum):
    HTTP = "http"
    TCP = "tcp"
    SSH = "ssh"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("Team", back_populates="members")
    submissions = relationship("Submission", back_populates="user")

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, index=True, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    score = Column(Integer, default=0)
    max_size = Column(Integer, default=5, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    members = relationship("User", back_populates="team")
    invitations = relationship("Invitation", back_populates="team")
    submissions = relationship("Submission", back_populates="team")
    challenge_solves = relationship("ChallengeSolve", back_populates="team")

class Invitation(Base):
    __tablename__ = "invitations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    email = Column(String(255), nullable=False)
    token = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(SQLEnum(InvitationStatus), default=InvitationStatus.PENDING)
    expires_at = Column(DateTime, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("Team", back_populates="invitations")

class Challenge(Base):
    __tablename__ = "challenges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(ChallengeCategory), nullable=False)
    difficulty = Column(SQLEnum(Difficulty), nullable=False)
    points = Column(Integer, nullable=False)
    initial_points = Column(Integer, nullable=False)
    min_points = Column(Integer, default=50, nullable=False)
    flag_hash = Column(String(255), nullable=False)
    author = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    hints = Column(JSON, default=list)
    files = Column(JSON, default=list)
    solves_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    submissions = relationship("Submission", back_populates="challenge")
    solves = relationship("ChallengeSolve", back_populates="challenge")

class ChallengeSolve(Base):
    __tablename__ = "challenge_solves"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("challenges.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    solved_at = Column(DateTime, default=datetime.utcnow)
    points_earned = Column(Integer, nullable=False)
    
    challenge = relationship("Challenge", back_populates="solves")
    team = relationship("Team", back_populates="challenge_solves")

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("challenges.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    flag = Column(String(500), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    challenge = relationship("Challenge", back_populates="submissions")
    team = relationship("Team", back_populates="submissions")
    user = relationship("User", back_populates="submissions")

class Service(Base):
    __tablename__ = "services"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    check_type = Column(SQLEnum(CheckType), nullable=False)
    expected_status = Column(Integer, default=200)
    check_interval = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    
    status_history = relationship("ServiceStatus", back_populates="service")

class ServiceStatus(Base):
    __tablename__ = "service_statuses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    is_up = Column(Boolean, nullable=False)
    response_time = Column(Integer)  # in milliseconds
    last_check = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text, nullable=True)
    
    service = relationship("Service", back_populates="status_history")
