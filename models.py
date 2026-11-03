from db import Base 
import os
from dotenv import load_dotenv
from datetime import datetime
import os
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Float,
    JSON,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# ==========================================
# TASK DEPENDENCIES
# ==========================================

task_dependencies = Table(
    "task_dependencies",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column(
        "depends_on_id",
        Integer,
        ForeignKey("tasks.id"),
        primary_key=True,
    ),
)


# ==========================================
# USER
# ==========================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    full_name = Column(String(100))
    bio = Column(Text)
    profile_picture = Column(String(255))

    skills = Column(JSON, default=list)
    interests = Column(JSON, default=list)
    preferences = Column(JSON, default=dict)

    experience_level = Column(String(30), default="beginner")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    teams = relationship("TeamMember", back_populates="user")
    owned_projects = relationship("Project", back_populates="owner")

    assigned_tasks = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assignee_id",
    )

    question_attempts = relationship(
        "QuestionAttempt",
        back_populates="user",
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )


# ==========================================
# TEAM
# ==========================================

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    description = Column(Text)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    invite_code = Column(String(50), unique=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan",
    )

    projects = relationship("Project", back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)

    role = Column(String(30), default="member")
    joined_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "team_id", name="unique_team_member"),
    )

    user = relationship("User", back_populates="teams")
    team = relationship("Team", back_populates="members")


# ==========================================
# COMPETITION
# ==========================================

class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    organizer = Column(String(150))
    description = Column(Text)

    theme = Column(String(150))
    website = Column(String(255))

    competition_type = Column(String(30), default="online")
    # online, offline, hybrid

    location = Column(String(150))

    registration_deadline = Column(DateTime)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    status = Column(String(30), default="upcoming")

    rules = Column(JSON, default=dict)
    judging_criteria = Column(JSON, default=dict)

    created_by = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="competition")

    registrations = relationship(
        "CompetitionRegistration",
        back_populates="competition",
        cascade="all, delete-orphan",
    )


# ==========================================
# COMPETITION REGISTRATION
# ==========================================

class CompetitionRegistration(Base):
    __tablename__ = "competition_registrations"

    id = Column(Integer, primary_key=True, index=True)

    competition_id = Column(
        Integer,
        ForeignKey("competitions.id"),
        nullable=False,
    )

    user_id = Column(Integer, ForeignKey("users.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))

    registration_status = Column(String(30), default="registered")
    registered_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "competition_id",
            "user_id",
            "team_id",
            name="unique_competition_registration",
        ),
    )

    competition = relationship(
        "Competition",
        back_populates="registrations",
    )


# ==========================================
# PROJECT
# ==========================================

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    description = Column(Text)

    problem_statement = Column(Text)
    proposed_solution = Column(Text)

    tech_stack = Column(JSON, default=list)

    status = Column(String(30), default="planning")
    priority = Column(String(30), default="medium")

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    competition_id = Column(Integer, ForeignKey("competitions.id"))

    deadline = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    owner = relationship("User", back_populates="owned_projects")
    team = relationship("Team", back_populates="projects")

    competition = relationship("Competition", back_populates="projects")

    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    simulations = relationship(
        "FailureSimulation",
        back_populates="project",
        cascade="all, delete-orphan",
    )


# ==========================================
# TASK
# ==========================================

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(150), nullable=False)
    description = Column(Text)

    status = Column(String(30), default="todo")
    priority = Column(String(30), default="medium")

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
    )

    assignee_id = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

    deadline = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    project = relationship("Project", back_populates="tasks")

    assignee = relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[assignee_id],
    )

    dependencies = relationship(
        "Task",
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.task_id,
        secondaryjoin=id == task_dependencies.c.depends_on_id,
    )


# ==========================================
# QUESTIONS
# Personalized Questions + Idea Test + Judge Arena
# ==========================================

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)
    question_text = Column(Text, nullable=False)

    category = Column(String(50), nullable=False)
    difficulty = Column(String(30), default="medium")

    expected_points = Column(JSON, default=list)
    evaluation_criteria = Column(JSON, default=dict)

    is_active = Column(Boolean, default=True)

    attempts = relationship(
        "QuestionAttempt",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        nullable=False,
    )

    project_id = Column(Integer, ForeignKey("projects.id"))

    answer = Column(Text)
    score = Column(Float)
    feedback = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="question_attempts")
    question = relationship("Question", back_populates="attempts")


# ==========================================
# MOCK HACKATHON
# ==========================================

class MockHackathon(Base):
    __tablename__ = "mock_hackathons"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(150), nullable=False)
    description = Column(Text)

    theme = Column(String(150))
    duration_minutes = Column(Integer, default=180)

    difficulty = Column(String(30), default="medium")

    rules = Column(JSON, default=dict)
    judging_rubric = Column(JSON, default=dict)
    stages = Column(JSON, default=list)

    created_by = Column(Integer, ForeignKey("users.id"))

    is_public = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    participants = relationship(
        "HackathonParticipant",
        back_populates="hackathon",
        cascade="all, delete-orphan",
    )


class HackathonParticipant(Base):
    __tablename__ = "hackathon_participants"

    id = Column(Integer, primary_key=True, index=True)

    hackathon_id = Column(
        Integer,
        ForeignKey("mock_hackathons.id"),
        nullable=False,
    )

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    team_id = Column(Integer, ForeignKey("teams.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))

    submission_title = Column(String(200))
    submission_description = Column(Text)
    submission_data = Column(JSON, default=dict)

    score = Column(Float)
    judge_feedback = Column(JSON, default=dict)

    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime)

    status = Column(String(30), default="registered")

    __table_args__ = (
        UniqueConstraint(
            "hackathon_id",
            "user_id",
            name="unique_mock_participant",
        ),
    )

    hackathon = relationship(
        "MockHackathon",
        back_populates="participants",
    )


# ==========================================
# FAILURE LAB
# ==========================================

class FailureSimulation(Base):
    __tablename__ = "failure_simulations"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
    )

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    scenario_name = Column(String(150), nullable=False)
    scenario_type = Column(String(50), nullable=False)

    description = Column(Text)

    input_data = Column(JSON, default=dict)
    affected_tasks = Column(JSON, default=list)
    fallback_plan = Column(JSON, default=list)
    results = Column(JSON, default=dict)

    risk_score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="simulations")


# ==========================================
# NOTIFICATIONS
# ==========================================

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(150), nullable=False)
    message = Column(Text)

    notification_type = Column(String(50))
    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
