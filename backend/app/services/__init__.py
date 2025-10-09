import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models import (
    User, Team, Invitation, Challenge, ChallengeSolve, 
    Submission, Service, ServiceStatus, UserRole, InvitationStatus
)
from app.schemas import (
    UserCreate, TeamCreate, ChallengeCreate, SubmissionCreate,
    InvitationCreate, ServiceCreate
)

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate, team_id: Optional[UUID] = None) -> User:
        # Check if user already exists
        if db.query(User).filter(User.email == user_data.email).first():
            raise ValueError("User with this email already exists")
        
        if db.query(User).filter(User.username == user_data.username).first():
            raise ValueError("User with this username already exists")
        
        user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=get_password_hash(user_data.password),
            team_id=team_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

class TeamService:
    @staticmethod
    def create_team(db: Session, team_data: TeamCreate, captain_id: UUID) -> Team:
        # Check if team name is unique
        if db.query(Team).filter(Team.name == team_data.name).first():
            raise ValueError("Team with this name already exists")
        
        team = Team(
            name=team_data.name,
            avatar_url=team_data.avatar_url
        )
        db.add(team)
        db.flush()  # Get team ID without committing
        
        # Update user to be captain of this team
        user = db.query(User).filter(User.id == captain_id).first()
        user.team_id = team.id
        user.role = UserRole.CAPTAIN
        
        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def create_invitation(db: Session, invitation_data: InvitationCreate, team_id: UUID, created_by: UUID) -> Invitation:
        # Check if user is already in a team
        existing_user = db.query(User).filter(User.email == invitation_data.email).first()
        if existing_user and existing_user.team_id:
            raise ValueError("User is already in a team")
        
        # Check for existing pending invitation
        existing_invitation = db.query(Invitation).filter(
            Invitation.email == invitation_data.email,
            Invitation.status == InvitationStatus.PENDING
        ).first()
        if existing_invitation:
            raise ValueError("Pending invitation already exists for this email")
        
        invitation = Invitation(
            team_id=team_id,
            email=invitation_data.email,
            token=str(uuid.uuid4()),
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_by=created_by
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        return invitation

class ChallengeService:
    @staticmethod
    def calculate_points(initial_points: int, solves_count: int, min_points: int = 50) -> int:
        decay_factor = initial_points * 0.05  # 5% decay per solve
        points = max(min_points, initial_points - (solves_count * decay_factor))
        return int(points)

    @staticmethod
    def create_challenge(db: Session, challenge_data: ChallengeCreate) -> Challenge:
        from app.core.security import get_password_hash
        
        challenge = Challenge(
            title=challenge_data.title,
            description=challenge_data.description,
            category=challenge_data.category,
            difficulty=challenge_data.difficulty,
            points=challenge_data.initial_points,
            initial_points=challenge_data.initial_points,
            min_points=challenge_data.min_points,
            flag_hash=get_password_hash(challenge_data.flag),
            author=challenge_data.author,
            is_active=challenge_data.is_active,
            hints=challenge_data.hints,
            files=challenge_data.files
        )
        db.add(challenge)
        db.commit()
        db.refresh(challenge)
        return challenge

    @staticmethod
    def submit_flag(db: Session, submission_data: SubmissionCreate, team_id: UUID, user_id: UUID) -> Submission:
        challenge = db.query(Challenge).filter(Challenge.id == submission_data.challenge_id).first()
        if not challenge:
            raise ValueError("Challenge not found")
        
        if not challenge.is_active:
            raise ValueError("Challenge is not active")
        
        # Check if already solved
        existing_solve = db.query(ChallengeSolve).filter(
            ChallengeSolve.challenge_id == submission_data.challenge_id,
            ChallengeSolve.team_id == team_id
        ).first()
        if existing_solve:
            raise ValueError("Challenge already solved by your team")
        
        # Verify flag
        is_correct = verify_password(submission_data.flag, challenge.flag_hash)
        
        submission = Submission(
            challenge_id=submission_data.challenge_id,
            team_id=team_id,
            user_id=user_id,
            flag=submission_data.flag,
            is_correct=is_correct
        )
        db.add(submission)
        
        if is_correct:
            # Update challenge points and solve count
            challenge.solves_count += 1
            challenge.points = ChallengeService.calculate_points(
                challenge.initial_points, 
                challenge.solves_count, 
                challenge.min_points
            )
            
            # Create solve record
            solve = ChallengeSolve(
                challenge_id=challenge.id,
                team_id=team_id,
                points_earned=challenge.points
            )
            db.add(solve)
            
            # Update team score
            team = db.query(Team).filter(Team.id == team_id).first()
            team.score += challenge.points
        
        db.commit()
        db.refresh(submission)
        return submission
