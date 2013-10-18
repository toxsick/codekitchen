
SERVER_NAME = "localhost:5000"
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
DOMAIN = {
    "jobs": {
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
}
