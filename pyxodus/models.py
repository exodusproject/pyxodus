"""
Declaration of models.

pyxodus
(c) 2016 XXXXXXXXXXXXXXX
Licensed under XXXXX, see LICENSE
"""

import enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


db = SQLAlchemy()


class ResourceTypes(enum.Enum):
    STATUS = "1"
    PHOTO = "2"
    # Add more here!


class Identity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    domain = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=func.now())

    resources = db.Relationship(
        "Resource", backref=db.backref("identity"))

    @property
    def fqn(self):
        """Returns the fully-qualified name for the identity (name@domain)."""
        return "{0}@{1}".format(self.name, self.domain)

    @property
    def json(self):
        """Return the Identity as a serializable hash."""
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "fqn": self.fqn
        }


class Resource(db.Model):
    """
    A basic representation of data, analogous to a single post, photo, etc.

    A Resource contains data objects (``ResourceData``) which in turn contain
    the actual data being exchanged. Each child data object equates to a
    specific version of the resource.

    The Resource object itself tracks a context for the information at-large,
    across versions: such as global resource ID, initial post/date time,
    tags and the like.
    """

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=func.now())
    identity_id = db.Column(
        db.Integer, db.ForeignKey("identity.id"), index=True
    )

    data = db.Relationship(
        "ResourceData", backref=db.backref("resource"))

    @property
    def current_version(self):
        """Return the most recent ResourceData."""
        return next(sorted(self.data, key=lambda x: x.version))

    @property
    def current_version_number(self):
        """Return the most recent version number of all child resources."""
        return self.current_version if self.current_version else 0

    @property
    def json(self):
        return {
            "id": self.id,
            "current_version_number": self.current_version_number,
            "data": [x.json for x in self.data]
        }


class ResourceData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
