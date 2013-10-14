from datetime import datetime, timedelta
import hashlib
from bson.json_util import dumps

class Config(object):
    # RFC 1123 (ex RFC 822)
    DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    SERVER_NAME = '127.0.0.1:5000'
    DOMAIN = {
        '/jobs': {},
    }
    URL_PREFIX = ""
    API_VERSION = ""
    ITEM_METHODS = ['GET']

    ALLOWED_FILTERS = ['*']         # filtering enabled by default
    PROJECTION = True               # projection enabled by default
    PAGINATION = True               # pagination enabled by default.
    PAGINATION_LIMIT = 50
    PAGINATION_DEFAULT = 25
    SORTING = True                  # sorting enabled by default.
    EMBEDDING = True                # embedding enabled by default

config = Config()


def set_defaults(resource):
    """ When not provided, fills individual resource settings with default
    or global configuration settings.

    .. versionchanged:: 0.1.1
       'default' values that could be assimilated to None (0, None, "")
       would be ignored.
       'dates' helper removed as datetime conversion is now handled by
       the eve.methods.common.data_parse function.

    .. versionchanged:: 0.1.0
      'embedding'.
       Support for optional HATEOAS.

    .. versionchanged:: 0.0.9
       'auth_username_field' renamed to 'auth_field'.
       Always include automatic fields despite of datasource projections.

    .. versionchanged:: 0.0.8
       'mongo_write_concern'

    .. versionchanged:: 0.0.7
       'extra_response_fields'

    .. versionchanged:: 0.0.6
       'datasource[projection]'
       'projection',
       'allow_unknown'

    .. versionchanged:: 0.0.5
       'auth_username_field'
       'filters',
       'sorting',
       'pagination'.

    .. versionchanged:: 0.0.4
       'defaults',
       'datasource',
       'public_methods',
       'public_item_methods',
       'allowed_roles',
       'allowed_item_roles'.

    .. versionchanged:: 0.0.3
       `item_title` default value.
    """
    settings = {}

    settings.setdefault('url', resource)

    settings.setdefault('allowed_filters',
                        config.ALLOWED_FILTERS)
    settings.setdefault('sorting', config.SORTING)
    settings.setdefault('embedding', config.EMBEDDING)
    settings.setdefault('pagination', config.PAGINATION)
    settings.setdefault('projection', config.PROJECTION)
    # TODO make sure that this we really need the test below
    #if settings['item_lookup']:
    #    item_methods = config.ITEM_METHODS
    #else:
    #    item_methods = eve.ITEM_METHODS
    item_methods = config.ITEM_METHODS
    settings.setdefault('item_methods', item_methods)

    # empty schemas are allowed for read-only access to resources
    schema = settings.setdefault('schema', {})
    #self.set_schema_defaults(schema)

    datasource = {}
    settings.setdefault('datasource', datasource)
    settings['datasource'].setdefault('source', resource)
    settings['datasource'].setdefault('filter', None)

    # enable retrieval of actual schema fields only. Eventual db
    # fields not included in the schema won't be returned.
    default_projection = {}
    default_projection.update(dict((field, 1) for (field) in schema))
    #projection = settings['datasource'].setdefault('projection',
    #                                               default_projection)
    # despite projection, automatic fields are always included.
    #projection[config.ID_FIELD]
    #projection[config.LAST_UPDATED]
    #projection[config.DATE_CREATED]

    # 'defaults' helper set contains the names of fields with
    # default values in their schema definition.

    # TODO support default values for embedded documents.
    settings['defaults'] = \
        set(field for field, definition in schema.items()
            if 'default' in definition)

    return settings


class ParsedRequest(object):
    """ This class, by means of its attributes, describes a client request.

    .. versonchanged:: 0.1.0
       'embedded' keyword.

    .. versionchanged:: 0.0.6
       Projection queries ('?projection={"name": 1}')
    """
    # `where` value of the query string (?where). Defaults to None.
    where = None

    # `projection` value of the query string (?projection). Defaults to None.
    projection = None

    # `sort` value of the query string (?sort). Defaults to None.
    sort = None

    # `page` value of the query string (?page). Defaults to 1.
    page = 1

    # `max_result` value of the query string (?max_results). Defaults to
    # `PAGINATION_DEFAULT` unless pagination is disabled.
    max_results = 0

    # `If-Modified-Since` request header value. Defaults to None.
    if_modified_since = None

    # `If-None_match` request header value. Defaults to None.
    if_none_match = None

    # `If-Match` request header value. Default to None.
    if_match = None

    # `embedded` value of the query string (?embedded). Defaults to None.
    embedded = None


def parse_request(request, rest_settings):
    """ Parses a client request, returning instance of :class:`ParsedRequest`
    containing relevant request data.

    :param resource: the resource currently being accessed by the client.

    .. versionchagend:: 0.1.0
       Support for embedded documents.

    .. versionchanged:: 0.0.6
       projection queries ('?projection={"name": 1}')

    .. versionchanged: 0.0.5
       Support for optional filters, sorting and pagination.
    """
    args = request.arguments
    headers = request.headers

    r = ParsedRequest()

    if rest_settings['allowed_filters']:
        r.where = args.get('where')
    if rest_settings['projection']:
        r.projection = args.get('projection')
    if rest_settings['sorting']:
        r.sort = args.get('sort')
    if rest_settings['embedding']:
        r.embedded = args.get('embedded')

    #max_results_default = config.PAGINATION_DEFAULT if \
    #    rest_settings['pagination'] else 0
    #try:
    #    r.max_results = int(float(args['max_results']))
    #    assert r.max_results > 0
    #except (ValueError, AssertionError):
    #    r.max_results = max_results_default

    if rest_settings['pagination']:
        # TODO should probably return a 400 if 'page' is < 1 or non-numeric
        if 'page' in args:
            try:
                r.page = abs(int(args.get('page'))) or 1
            except ValueError:
                pass

        # TODO should probably return a 400 if 'max_results' < 1 or
        # non-numeric
        if r.max_results > config.PAGINATION_LIMIT:
            r.max_results = config.PAGINATION_LIMIT

    if headers:
        r.if_modified_since = weak_date(headers.get('If-Modified-Since'))
        # TODO if_none_match and if_match should probably be validated as
        # valid etags, returning 400 on fail. Not sure however since
        # we're just going to use these for string-type comparision
        r.if_none_match = headers.get('If-None-Match')
        r.if_match = headers.get('If-Match')

    return r


def weak_date(date):
    """ Returns a RFC-1123 string corresponding to a datetime value plus
    a 1 second timedelta. This is needed because when saved, documents
    LAST_UPDATED values have higher resolution than If-Modified-Since's, which
    is limited to seconds.

    :param date: the date to be adjusted.
    """
    return str_to_date(date) + timedelta(seconds=1) if date else None


def str_to_date(string):
    """ Converts a RFC-1123 string to the corresponding datetime value.

    :param string: the RFC-1123 string to convert to datetime value.
    """
    return datetime.strptime(string, config.DATE_FORMAT) if string else None


def date_to_str(date):
    """ Converts a datetime value to the corresponding RFC-1123 string.

    :param date: the datetime value to convert.
    """
    return datetime.strftime(date, config.DATE_FORMAT) if date else None


def item_etag(value):
    """ Computes and returns a valid ETag for the input value.

    :param value: the value to compute the ETag with.

    .. versionchanged:: 0.0.4
       Using bson.json_util.dumps over str(value) to make etag computation
       consistent between different runs and/or server instances (#16).
    """
    h = hashlib.sha1()
    h.update(dumps(value, sort_keys=True).encode('utf-8'))
    return h.hexdigest()


def resource_link(resource):
    """ Returns a link to a resource endpoint.

    :param resource: the resource name.

    .. versionchanged:: 0.0.3
       Now returning a JSON link
    """
    return {'title': '%s' % config.URLS[resource],
            'href': '%s' % resource_uri(resource)}


def item_link(resource, item_id):
    """ Returns a link to a item endpoint.

    :param resource: the resource name.
    :param item_id: the item unique identifier.

    .. versionchanged:: 0.1.0
       No more trailing slashes in links.

    .. versionchanged:: 0.0.3
       Now returning a JSON link
    """
    return {'title': '%s' % config.DOMAIN[resource]['item_title'],
            'href': '%s/%s' % (resource_uri(resource), item_id)}


def home_link():
    """ Returns a link to the API entry point/home page.

    .. versionchanged:: 0.1.1
       Handle the case of SERVER_NAME being None.

    .. versionchanged:: 0.0.3
       Now returning a JSON link.
    """
    server_name = config.SERVER_NAME if config.SERVER_NAME else ''
    return {'title': 'home',
            'href': '%s%s' % (server_name, api_prefix())}


def api_prefix(url_prefix=None, api_version=None):
    """ Returns the prefix to API endpoints, according to the URL_PREFIX and
    API_VERSION  configuration settings.

    :param url_prefix: the prefix string. If `None`, defaults to the current
                       :class:`~eve.flaskapp` configuration setting.
                       The class itself will call this function while
                       initializing. In that case, it will pass its settings
                       as arguments (as they are not externally available yet)
    :param api_version: the api version string. If `None`, defaults to the
                        current :class:`~eve.flaskapp` configuration setting.
                        The class itself will call this function while
                        initializing. In that case, it will pass its settings
                        as arguments (as they are not externally available yet)

    .. versionadded:: 0.0.3
    """

    if url_prefix is None:
        url_prefix = config.URL_PREFIX
    if api_version is None:
        api_version = config.API_VERSION

    prefix = '/%s' % url_prefix if url_prefix else ''
    version = '/%s' % api_version if api_version else ''
    return prefix + version

def resource_uri(resource):
    """ Returns the absolute URI to a resource.

    .. versionchanged:: 0.1.1
       Handle the case of SERVER_NAME being None.

    .. versionchanged:: 0.1.0
       No more trailing slashes in links.

    :param resource: the resource name.
    """
    server_name = config.SERVER_NAME if config.SERVER_NAME else ''
    return '%s%s/%s' % (server_name, api_prefix(),
                        config.URLS[resource])
