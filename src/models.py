from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all, delete")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }
    
class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="planet", cascade="all, delete")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }
    
class Character(db.Model):
    __tablename__ = "character"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="character", cascade="all, delete")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }

class Favorite(db.Model):
    __tablename__ = "favorite"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"))
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"))

    user: Mapped["User"] = relationship(back_populates="favorites")
    character: Mapped["Character"] = relationship(back_populates="favorites")
    planet: Mapped["Planet"] = relationship(back_populates="favorites")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
        }