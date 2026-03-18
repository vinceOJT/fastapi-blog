from __future__ import annotations # lower then ver 3.14
# For older version of python this is use to annotate forward reference
# Below we reference Post bfore it's even created, this is called forward reference


from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


# Blueprint for creating users

class User(Base):
    # Creating database table with required parameters
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None,
    )



    # This is a relationship that creates a one to many relationship
    # So one use can have many posts
    posts: Mapped[list[Post]] = relationship(
        back_populates="author",
          cascade="all, delete-orphan", # This not only permanently deletes the user but also deletes their posts
          ) 
    # back_populates, gets the posts of the user then only shows their posts no one else's



    # Checks if user uploads an image, if so return that image if not return a default image
    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"












# Blueprint for creating posts
class Post(Base):
    # Creating table for posts


    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), # ref to the users table 
        nullable=False,
        index=True,
        # Without the index parameter, it manually searches the user.id in the foreign table

 
    )
    # datetime creation
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # This is many post one user
    author: Mapped[User] = relationship(back_populates="posts")
    
