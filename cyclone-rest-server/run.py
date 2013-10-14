import cyclone.web
import sys

from twisted.internet import reactor
from twisted.python import log
from common import last_updated, date_created 
from utils import parse_request, item_etag, home_link, set_defaults #resource_link
from render import render_json


class CycloneRestHandler(cyclone.web.RequestHandler):

    def initialize(self, rest_settings):
        self.rest_settings = rest_settings
    
    def get(self, item_id=None):
        req = parse_request(self.request, self.rest_settings)

        response = {}

        data = [{"user": "hanso"}, {"user": "pie"}]

        if item_id:
            items = [i for i in data if i["user"] == item_id]
        else:
            items = data

        for item in items:

            item["updated"] = last_updated(item)
            item["created"] = date_created(item)
            item['etag'] = item_etag(item)

        response["items"] = items

        response['links'] = self._pagination_links(None, None, len(items))

        self.set_header('Content-Type', 'application/json')
        
        self.write(render_json(response))

    def post(self, instance_id=None, action=None):
        return self.rest_handler.post(instance_id=instance_id, action=action)

    def put(self, instance_id):
        return self.rest_handler.put(instance_id=instance_id)

    def delete(self, instance_id):
        return self.rest_handler.delete(instance_id=instance_id)

    def _pagination_links(self, resource, req, documents_count):
        """Returns the appropriate set of resource links depending on the
        current page and the total number of documents returned by the query.

        :param resource: the resource name.
        :param req: and instace of :class:`eve.utils.ParsedRequest`.
        :param document_count: the number of documents returned by the query.

        .. versionchanged:: 0.0.8
           Link to last page is provided if pagination is enabled (and the current
           page is not the last one).

        .. versionchanged:: 0.0.7
           Support for Rate-Limiting.

        .. versionchanged:: 0.0.5
           Support for optional pagination.

        .. versionchanged:: 0.0.3
           JSON links
        """
        #_links = {'parent': home_link(), 'self': resource_link(resource)}
        _links = {'parent': home_link()}

        """
        if documents_count and config.DOMAIN[resource]['pagination']:
            if req.page * req.max_results < documents_count:
                q = querydef(req.max_results, req.where, req.sort, req.page + 1)
                _links['next'] = {'title': 'next page', 'href': '%s%s' %
                                  (resource_uri(resource), q)}

                # in python 2.x dividing 2 ints produces an int and that's rounded
                # before the ceil call. Have to cast one value to float to get
                # a correct result. Wonder if 2 casts + ceil() call are actually
                # faster than documents_count // req.max_results and then adding
                # 1 if the modulo is non-zero...
                last_page = int(math.ceil(documents_count
                                          / float(req.max_results)))
                q = querydef(req.max_results, req.where, req.sort, last_page)
                _links['last'] = {'title': 'last page', 'href': '%s%s'
                                  % (resource_uri(resource), q)}

            if req.page > 1:
                q = querydef(req.max_results, req.where, req.sort, req.page - 1)
                _links['prev'] = {'title': 'previous page', 'href': '%s%s' %
                                  (resource_uri(resource), q)}
        """

        return _links


#class MyRestHandler(cyclone.web.RequestHandler, python_rest_handler.RestRequestHandler):
#    data_manager = MongoDBDataManager


if __name__ == "__main__":
    handlers = [
        #(r"/jobs/?", CycloneRestHandler, dict(rest_settings=set_defaults("/jobs"))),
        (r"/jobs/?([A-Za-z0-9]+/?)?", CycloneRestHandler, dict(rest_settings=set_defaults("/jobs"))),
        #(r"/jobs/?", CycloneRestHandler, dict(rest_settings=set_defaults("/jobs"))),
        #(r"/jobs/([A-Za-z0-9]+)/?", CycloneRestHandler, dict(rest_settings={})),
        #(r"/jobs/([A-Za-z0-9]+)/edit/?", CycloneRestHandler, dict(rest_settings={}))
        #(r"/jobs/?", CycloneRestHandler)
    ]
    application = cyclone.web.Application(handlers)

    log.startLogging(sys.stdout)
    reactor.listenTCP(8888, application, interface="127.0.0.1")
    reactor.run()
