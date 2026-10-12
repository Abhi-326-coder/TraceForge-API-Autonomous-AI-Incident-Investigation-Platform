from datetime import datetime
from sqlalchemy import JSON

from sqlalchemy import DateTime, ForeignKey, String, Text, Integer, Column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import (
    Vector,
)
from app.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    incidents: Mapped[list["Incident"]] = relationship(
        back_populates="project"
    )
    
    connections: Mapped[list["ProjectConnection"]] = relationship(
    back_populates="project",
    cascade="all, delete-orphan",
    )


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    external_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    service: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    project: Mapped["Project"] = relationship(
        back_populates="incidents"
    )
    
    investigations: Mapped[list["Investigation"]] = relationship(
    back_populates="incident",
    cascade="all, delete-orphan",
    )
    
class ProjectConnection(Base):
    __tablename__ = "project_connections"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    connection_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    project: Mapped["Project"] = relationship(
        back_populates="connections"
    )
    
class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="CREATED",
    )

    current_stage: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="CREATED",
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    incident: Mapped["Incident"] = relationship(
        back_populates="investigations"
    )
    
    evidence: Mapped[list["Evidence"]] = relationship(
    back_populates="investigation",
    cascade="all, delete-orphan",
    )
    
class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    investigation_id: Mapped[int] = mapped_column(
        ForeignKey("investigations.id"),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source_reference: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    investigation: Mapped["Investigation"] = relationship(
        back_populates="evidence",
    )

class KnowledgeDocument(Base):

    __tablename__ = "knowledge_documents"

    id = Column(
        Integer,
        primary_key=True,
    )

    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
    )

    title = Column(
        String,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    source = Column(
        String,
        nullable=False,
    )

    chunk_index = Column(
        Integer,
        nullable=False,
    )

    embedding = Column(
        Vector(768),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )


class PatchApproval(Base):
    __tablename__ = "patch_approvals"

    id = Column(Integer, primary_key=True, index=True)

    investigation_id = Column(
        Integer,
        ForeignKey("investigations.id"),
        nullable=False,
        index=True,
    )

    patch_summary = Column(Text, nullable=False)
    diff = Column(Text, nullable=False)
    changed_files = Column(JSON, nullable=False)
    tests_to_run = Column(JSON, nullable=False)
    risks = Column(JSON, nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="PENDING",
        index=True,
    )

    decision_note = Column(Text, nullable=True)
    decided_by = Column(String(255), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    decided_at = Column(DateTime(timezone=True), nullable=True)
    proposed_files = Column(JSON, nullable=False, default=dict)
    patch_sha256 = Column(String(64), nullable=True)
    github_branch = Column(String(255), nullable=True)
    github_commit_sha = Column(String(40), nullable=True)
    github_pr_number = Column(Integer, nullable=True)
    github_pr_url = Column(String(500), nullable=True)