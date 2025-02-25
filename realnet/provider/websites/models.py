from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class ContentStatus(enum.Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'

class Website(Base):
    __tablename__ = 'websites'

    id = Column(Integer, primary_key=True)
    domain = Column(String(255), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    theme = Column(String(255))
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    wordpress_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pages = relationship('Page', back_populates='website', cascade='all, delete-orphan')
    posts = relationship('Post', back_populates='website', cascade='all, delete-orphan')

class Page(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey('websites.id'), nullable=False)
    path = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    layout = Column(String(255))
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    meta = Column(JSON)
    wordpress_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    website = relationship('Website', back_populates='pages')

    __table_args__ = (
        # Ensure path is unique per website
        UniqueConstraint('website_id', 'path', name='uq_page_website_path'),
    )

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey('websites.id'), nullable=False)
    path = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text)
    author = Column(String(255))
    categories = Column(JSON)  # Stored as array
    tags = Column(JSON)  # Stored as array
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    meta = Column(JSON)
    wordpress_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    website = relationship('Website', back_populates='posts')

    __table_args__ = (
        # Ensure path is unique per website
        UniqueConstraint('website_id', 'path', name='uq_post_website_path'),
    )

def init_db(engine):
    """Initialize database tables"""
    Base.metadata.create_all(engine)
