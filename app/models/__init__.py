# init file for models package
# add all models to app/models directory and import them here

from .User import User
from .AuthEvent import AuthEvent

# Names model is only being used for testing
# from .Names import Names


# To migrate any new models or changes to existing schema, run the following Flask-Migrate commands:
# flask db migrate -m "message here"     -- this creates a new migration script
# flask db upgrade                       -- this runs the migration script and updates the database

# additional commands:
# flask db history                       -- this shows the history of migrations
# flask db current                       -- this shows the current version of the database
# flask db downgrade                     -- this reverts the database to the previous version
# flask db stamp head                    -- this marks the current version as the head
# flask db history                       -- this shows the history of migrations

