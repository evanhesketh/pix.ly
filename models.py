"""SQL Alchemy for pix.ly"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Image(db.Model):
    """Image in the system"""

    __tablename__ = "images"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    url = db.Column(
        db.Text,
        nullable=False
    )

    make = db.Column(
        db.Text
    )

    model = db.Column(
        db.Text
    )

    date = db.Column(
        db.Text
    )


    @classmethod
    def add_image(cls, url, make, model, date):
        """Add image to db"""

        image = Image(
            url=url,
            make=make,
            model=model,
            date=date
        )

        db.session.add(image)



