from eveclone import handlers

jobs = {
    "pattern": r"/jobs/?([A-Za-z0-9]+/?)?",
    "handler": handlers.RestHandler,
    "settings": {
    }
}

DOMAIN = {
    "jobs": jobs
}
