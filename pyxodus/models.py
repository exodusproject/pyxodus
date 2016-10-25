"""
Declaration of models.

pyxodus
(c) 2016 XXXXXXXXXXXXXXX
Licensed under XXXXX, see LICENSE
"""

import enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.types import JSON


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
    specific version of the master data of the resource.

    The Resource object itself tracks metadata for the information at-large,
    across versions: such as global resource ID, initial post/date time,
    tags and the like.
    """

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=func.now())
    identity_id = db.Column(
        db.Integer, db.ForeignKey("identity.id"), index=True
    )

    data = db.Relationship(
        "ResourceData", backref=db.backref("resource")
    )
    attachments = db.Relationship(
        "ResourceAttachment", backref=db.backref("resource")
    )

    @property
    def current_version(self):
        """Return the most recent ResourceData."""
        return next(sorted(self.data, key=lambda x: x.version))

    @property
    def current_version_number(self):
        """Return the most recent version number of all child resources."""
        return self.current_version.version if self.current_version else 0

    @property
    def json(self):
        return {
            "id": self.id,
            "current_version": self.current_version_number,
            "created_at": self.created_at.isoformat(),
            "data": {x.version: x.json for x in self.data},
            "attachments": {x.version: x.json for x in self.attachments}
        }


class ResourceData(db.Model):
    """
    Contains the raw data being exchanged with a Resource.

    The ResourceData object is a versioned iteration of the actual master data
    associated with a Resource. It contains metadata for this iteration of the
    data as well as the data itself as a JSON-encoded document.
    """
    __tablename__ = "resource_data"
    id = db.Column(db.Integer, primary_key=True)

    version = db.Column(db.Integer, index=True)
    created_at = db.Column(db.DateTime, default=func.now(), index=True)
    resource_type = db.Column(db.String, index=True)
    resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"))

    data = db.Column(JSON)

    @property
    def json(self):
        return {
            "resource_type": self.resource_type,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "data": self.data
        }


class ResourceAttachment(db.Model):
    """
    Contains linked data being exchanged with a Resource.

    The ResourceAttachment object is a versioned iteration of data
    accompanying a Resource, such as a link to an image, external link or
    resource.
    """
    __tablename__ = "resource_attachment"
    id = db.Column(db.Integer, primary_key=True)

    version = db.Column(db.Integer, index=True)
    created_at = db.Column(db.DateTime, default=func.now())
    attachment_type = db.Column(db.String)
    resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"))

    data = db.Column(JSON)

    @property
    def json(self):
        return {
            "attachment_type": self.attachment_type,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "data": self.data
        }
