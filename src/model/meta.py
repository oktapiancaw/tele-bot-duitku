# Copyright (C) 2026 Oktapiancaw
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

from src.configs import config


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    category_type: Mapped[str] = mapped_column(String, nullable=False, default="keluar")
    __table_args__ = (
        UniqueConstraint(
            "name", "user_id", "category_type", name="uq_category_name_user_id"
        ),
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )


class BillingMethod(Base):
    __tablename__ = "billing_methods"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    __table_args__ = (
        UniqueConstraint("name", "user_id", name="uq_billing_name_user_id"),
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="billing_method", cascade="all, delete-orphan"
    )


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    billing_method_id: Mapped[int] = mapped_column(ForeignKey("billing_methods.id"))

    category: Mapped["Category"] = relationship(back_populates="transactions")
    billing_method: Mapped["BillingMethod"] = relationship(
        back_populates="transactions"
    )


engine = create_engine(config.db.uri_string(base="postgresql+psycopg"), echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
