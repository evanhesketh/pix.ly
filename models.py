"""SQL Alchemy for pix.ly"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Photo(db.Model):
    """Image in the system"""

    __tablename__ = "photos"

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

        photo = Photo(
            url=url,
            make=make,
            model=model,
            date=date
        )

        db.session.add(photo)

def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """
    app.app_context().push()
    db.app = app
    db.init_app(app)



