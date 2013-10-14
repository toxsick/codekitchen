from datetime import datetime


def last_updated(item):
    """Fixes item's LAST_UPDATED field value. Flask-PyMongo returns
    timezone-aware values while stdlib datetime values are timezone-naive.
    Comparisions between the two would fail.

    If LAST_UPDATE is missing we assume that it has been created outside of the
    API context and inject a default value, to allow for proper computing of
    Last-Modified header tag. By design all items return a LAST_UPDATED
    (and we don't want to break existing clients).

    :param item: the item to be processed.

    .. versionchanged:: 0.1.0
       Moved to common.py and renamed as public, so it can also be used by edit
       methods (via get_document()).

    .. versionadded:: 0.0.5
    """
    if "updated" in item:
        return item["updated"].replace(tzinfo=None)
    else:
        return epoch()


def date_created(item):
    """If DATE_CREATED is missing we assume that it has been created outside of
    the API context and inject a default value. By design all items
    return a DATE_CREATED (and we dont' want to break existing clients).

    :param item: the item to be processed.

    .. versionchanged:: 0.1.0
       Moved to common.py and renamed as public, so it can also be used by edit
       methods (via get_documents()).

    .. versionadded:: 0.0.5
    """
    return item["created"] if "created" in item else epoch()


def epoch():
    """ A datetime.min alternative which won't crash on us.

    .. versionchanged:: 0.1.0
       Moved to common.py and renamed as public, so it can also be used by edit
       methods (via get_documents()).

    .. versionadded:: 0.0.5
    """
    return datetime(1970, 1, 1)



