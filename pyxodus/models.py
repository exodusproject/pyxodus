"""
Declaration of models.

pyxodus
(c) 2016 XXXXXXXXXXXXXXX
Licensed under XXXXX, see LICENSE
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.types import JSON


db = SQLAlchemy()


class Identity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    domain = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=func.now())

    resources = db.Relationship(
        "Resource", backref=db.backref("identity", uselist=False))

    @property
    def fqn(self):
        """Returns the fully-qualified name for the identity (name@domain)."""
        return "{0}@{1}".format(self.name, self.domain)

    @property
    def json(self):
        """Return the Identity as a serializable dict."""
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
    metadata = db.Column(JSON)
    references = db.relationship(
        "ResourceReference",
        backref=db.backref("from_resource", uselist=False),
    )
    referenced_from = db.relationship(
        "ResourceReference",
        backref=db.backref("to_resource", uselist=False),
    )
    mentions = db.relationship(
        "ResourceMention", backref=db.backref("resource", uselist=False)
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
            "data": {str(x.version): x.json for x in self.data},
            "references": {
                str(x.position): x.resource_id for x in self.references
            },
            "mentions": {
                str(x.position): x.identity_id for x in self.mentions
            },
            "meta": self.metadata
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
        data = {
            "resource_type": self.resource_type,
            "created_at": self.created_at.isoformat()
        }
        return {**data, **self.data}


class ResourceReference(db.Model):
    """
    A reference from one resource to another.

    Can be used to create message threads, post attachments and the like.
    """
    __tablename__ = "resource_reference"
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer)
    from_resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"))
    to_resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"))


class ResourceMention(db.Model):
    """
    A reference from one resource to one identity.

    Can be used for status mentions (@-replys), photo tagging and the like.
    """
    __tablename__ = "resource_mention"
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer)
    resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"))
    identity_id = db.Column(db.Integer, db.ForeignKey("identity.id"))
    identity = db.relationship(
        "Identity", uselist=False, backref=db.backref("Mentions")
    )
