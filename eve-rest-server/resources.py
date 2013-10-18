from eveclone import handlers

jobs = {
    "handler": handlers.RestHandler,
    "schema": {
        # Schema definition, based on Cerberus grammar. Check the Cerberus project
        # (https://github.com/nicolaiarocci/cerberus) for details.
        'firstname': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 10,
        }
    }
}

#HATEOAS = False
SERVER_NAME = "localhost:8888"
DOMAIN = {
    "jobs": jobs
}
