"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create teams table
    op.create_table('teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('registration_date', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('captain_id', sa.Integer(), nullable=True),
        sa.Column('penalty_minutes', sa.Integer(), nullable=True),
        sa.Column('extended_until', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)
    op.create_index(op.f('ix_teams_name'), 'teams', ['name'], unique=True)

    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('language', sa.String(length=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create challenges table
    op.create_table('challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('flag', sa.String(length=500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_challenges_id'), 'challenges', ['id'], unique=False)

    # Create submissions table
    op.create_table('submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('flag', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('points_awarded', sa.Integer(), nullable=True),
        sa.Column('is_first_blood', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], )
    )
    op.create_index(op.f('ix_submissions_id'), 'submissions', ['id'], unique=False)

    # Create services table
    op.create_table('services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('last_checked', sa.DateTime(), nullable=True),
        sa.Column('last_status_change', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], )
    )
    op.create_index(op.f('ix_services_id'), 'services', ['id'], unique=False)

    # Create team_invites table
    op.create_table('team_invites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('token', sa.String(length=100), nullable=False),
        sa.Column('invited_by', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id'], )
    )
    op.create_index(op.f('ix_team_invites_id'), 'team_invites', ['id'], unique=False)
    op.create_index(op.f('ix_team_invites_token'), 'team_invites', ['token'], unique=True)

    # Create competitions table
    op.create_table('competitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('penalty_minutes', sa.Integer(), nullable=True),
        sa.Column('service_check_interval', sa.Integer(), nullable=True),
        sa.Column('max_team_size', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_competitions_id'), 'competitions', ['id'], unique=False)

    # Add foreign key constraint for teams.captain_id
    op.create_foreign_key('fk_teams_captain_id', 'teams', 'users', ['captain_id'], ['id'])

def downgrade() -> None:
    op.drop_table('competitions')
    op.drop_table('team_invites')
    op.drop_table('services')
    op.drop_table('submissions')
    op.drop_table('challenges')
    op.drop_table('users')
    op.drop_table('teams')