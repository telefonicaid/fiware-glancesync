# -- encoding: utf-8 --
#
# Copyright 2015-2016 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-WARE project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es
#
# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from fiwareglancesync.app.app import db


# Define a base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    current_date = db.func.current_timestamp()
    date_created = db.Column(db.DateTime,  default=current_date)
    date_modified = db.Column(db.DateTime,  default=current_date, onupdate=current_date)


# Define a User model
class User(Base):
    __tablename__ = 'auth_user'

    # Region name: Identification data
    region = db.Column(db.String(128), nullable=False, unique=False)

    # User name: Identification data
    name = db.Column(db.String(128), nullable=False, unique=False)

    # Task Id: Identificator of the synchronization task
    task_id = db.Column(db.String(128), nullable=False, unique=True)

    # Authorisation Data: role
    role = db.Column(db.String(128), nullable=False)

    # Status of synchronisation operation
    status = db.Column(db.String(128), nullable=False)

    # New instance instantiation procedure
    def __init__(self, region, name, task_id, role, status):
        self.region = region
        self.name = name
        self.task_id = task_id
        self.role = role
        self.status = status

    def __repr__(self):
        return '<User %r>' % self.name

    def change_status(self, new_status):
        self.status = new_status
        self.date_modified = db.func.current_timestamp()
