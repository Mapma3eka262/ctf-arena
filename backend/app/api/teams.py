from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_captain
from app.models import User, Team, Invitation, InvitationStatus
from app.schemas import (
    TeamResponse, InvitationCreate, InvitationResponse, 
    TeamCreate, UserResponse
)
from app.services import TeamService

router = APIRouter()

@router.get("/my", response_model=TeamResponse)
def get_my_team(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not in a team"
        )
    
    team = db.query(Team).filter(Team.id == current_user.team_id).first()
    return team

@router.post("/invites", response_model=InvitationResponse)
def create_invitation(
    invitation_data: InvitationCreate,
    current_user: User = Depends(require_captain),
    db: Session = Depends(get_db)
):
    if not current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not in a team"
        )
    
    try:
        invitation = TeamService.create_invitation(
            db, invitation_data, current_user.team_id, current_user.id
        )
        return invitation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/invites", response_model=List[InvitationResponse])
def get_team_invitations(
    current_user: User = Depends(require_captain),
    db: Session = Depends(get_db)
):
    if not current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not in a team"
        )
    
    invitations = db.query(Invitation).filter(
        Invitation.team_id == current_user.team_id
    ).all()
    return invitations

@router.put("/invites/{invitation_id}")
def accept_invitation(
    invitation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )
    
    if invitation.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation is not for you"
        )
    
    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation is not pending"
        )
    
    if current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already in a team"
        )
    
    # Add user to team
    current_user.team_id = invitation.team_id
    invitation.status = InvitationStatus.ACCEPTED
    db.commit()
    
    return {"message": "Successfully joined the team"}

@router.delete("/invites/{invitation_id}")
def cancel_invitation(
    invitation_id: UUID,
    current_user: User = Depends(require_captain),
    db: Session = Depends(get_db)
):
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )
    
    if invitation.team_id != current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your team's invitation"
        )
    
    db.delete(invitation)
    db.commit()
    
    return {"message": "Invitation cancelled"}

@router.delete("/members/{user_id}")
def remove_member(
    user_id: UUID,
    current_user: User = Depends(require_captain),
    db: Session = Depends(get_db)
):
    if not current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not in a team"
        )
    
    user_to_remove = db.query(User).filter(
        User.id == user_id,
        User.team_id == current_user.team_id
    ).first()
    
    if not user_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in your team"
        )
    
    if user_to_remove.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself"
        )
    
    user_to_remove.team_id = None
    if user_to_remove.role == UserRole.CAPTAIN:
        user_to_remove.role = UserRole.MEMBER
    
    db.commit()
    
    return {"message": "Member removed from team"}

@router.post("/transfer-captain")
def transfer_captain(
    new_captain_id: UUID,
    current_user: User = Depends(require_captain),
    db: Session = Depends(get_db)
):
    if not current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not in a team"
        )
    
    new_captain = db.query(User).filter(
        User.id == new_captain_id,
        User.team_id == current_user.team_id
    ).first()
    
    if not new_captain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in your team"
        )
    
    # Transfer captain role
    current_user.role = UserRole.MEMBER
    new_captain.role = UserRole.CAPTAIN
    
    db.commit()
    
    return {"message": "Captain role transferred successfully"}