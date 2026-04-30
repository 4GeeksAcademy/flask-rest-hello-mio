from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Table, Column, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()

likes_table = Table(
    "likes",
    db.Model.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("post_id", ForeignKey("post.id"), primary_key=True)
)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(80), nullable=False)
    lastname: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    liked_posts: Mapped[list["Post"]] = relationship("Post", secondary=likes_table, back_populates="liked_by")
    
    following: Mapped[list["Follower"]] = relationship(
        "Follower",
        foreign_keys="Follower.user_from_id",
        back_populates="follower",
        cascade="all, delete-orphan"
    )
    followers: Mapped[list["Follower"]] = relationship(
        "Follower",
        foreign_keys="Follower.user_to_id",
        back_populates="followed",
        cascade="all, delete-orphan"
    )
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "posts_count": len(self.posts),
            "followers_count": len(self.followers),
            "following_count": len(self.following)
        }


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    caption: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    author: Mapped["User"] = relationship("User", back_populates="posts")
    liked_by: Mapped[list["User"]] = relationship("User", secondary=likes_table, back_populates="liked_posts")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    
    def serialize(self):
        return {
            "id": self.id,
            "caption": self.caption,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user_id": self.user_id,
            "author_username": self.author.username if self.author else None,
            "likes_count": len(self.liked_by),
            "comments_count": len(self.comments)
        }


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)
    
    author: Mapped["User"] = relationship("User")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    
    def serialize(self):
        return {
            "id": self.id,
            "comment_text": self.comment_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "author_id": self.author_id,
            "author_username": self.author.username if self.author else None,
            "post_id": self.post_id
        }


class Follower(db.Model):
    user_from_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    user_to_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    follower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_from_id],
        back_populates="following"
    )
    followed: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_to_id],
        back_populates="followers"
    )
    
    def serialize(self):
        return {
            "user_from_id": self.user_from_id,
            "user_to_id": self.user_to_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "follower_username": self.follower.username if self.follower else None,
            "followed_username": self.followed.username if self.followed else None
        }