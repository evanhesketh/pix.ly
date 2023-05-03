"""SQL Alchemy for pix.ly"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Image(db.Model):
    """Image in the system"""

    __tablename__ = "images"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    