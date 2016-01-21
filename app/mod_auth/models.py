# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from app import db

__author__ = 'fla'


# Define a base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


# Define a User model
class User(Base):
    __tablename__ = 'auth_user'

    # User name: Identification data
    name = db.Column(db.String(128), nullable=False, unique=True)

    # Authorisation Data: role
    role = db.Column(db.String(128), nullable=False)

    # Status of synchronisation operation
    status = db.Column(db.String(128), nullable=False)

    # New instance instantiation procedure
    def __init__(self, name, role, status):
        self.name = name
        self.role = role
        self.status = status

    def __repr__(self):
        return '<User %r>' % self.name


class TokenModel():
    """
    Define a Token model (in current version not stored in DB.
    """
    tenant = None
    id = None
    expires = None

    def __init__(self, tenant, id, expires):
        self.tenant = tenant
        self.id = id
        self.expires = expires


class Image():
    """
    Define a Image model to be used in the response of the GlaceSync API.
    id: Image id corresponding to the Glance service in a region (e.g. "3cfeaf3f0103b9637bb3fcfe691fce1e").
    name: Name of the image in the master (Spain2) node (e.g. "base_ubuntu_14.04").
    status: Status of the synchronization of the images
       (see https://github.com/telefonicaid/fiware-glancesync#checking-status for more information).
    message = Error message of the synchronization or null if all was ok.
    glancestatus = GlanceSync synchronization status
    """

    id = None       # Ex id = "3cfeaf3f0103b9637bb3fcfe691fce1e",
    name = None     # Ex name = "base_ubuntu_14.04",
    status = None   # Ex status = "ok",
    message = None  # Ex message = null,

    # Constants associated to the glancesync status
    OK = 'ok'
    OK_STALLED_CHECKSUM = 'ok_stalled_checksum'
    ERROR_CHECKSUM = 'error_checksum'
    ERROR_AMI = 'error_ami'
    PENDING_METADATA = 'pending_metadata'
    PENDING_UPLOAD = 'pending_upload'
    PENDING_REPLACE = 'pending_replace'
    PENDING_RENAME = 'pending_rename'
    PENDING_AMI = 'pending_ami'

    # GlanceSync synchronization status
    glancestatus = {'ok', 'ok_stalled_checksum',
                    'error_checksum', 'error_ami',
                    'pending_metadata', 'pending_upload', 'pending_replace', 'pending_rename', 'pending_ami'}

    def __init__(self, identify, name, status, message):
        """
        Default constructor of the class.
        :param identify: Id of the image.
        :param name: Name of the image.
        :param status: Status of the synchronization process.
        :param message: Message about the proccess if something was wrong.
        :return:
        """
        self.id = identify
        self.name = name
        self.status = status
        self.message = message

        try:
            self.check_status()
        except ValueError as ex:
            raise ex


    def check_status(self):
        if self.status not in self.glancestatus:
            raise ValueError('Error, the status does not correspond to any of the defined values',
                             self.status, self.glancestatus)

        return True



