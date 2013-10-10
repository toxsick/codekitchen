import cyclone.web
import sys

from twisted.internet import reactor
from twisted.python import log

from forms import ExampleForm


class CycloneRestHandler(cyclone.web.RequestHandler):
    
    def get(self, instance_id=None, edit=False):
        print instance_id
        print edit
        form = ExampleForm(self)
        if form.validate():
            self.write("yes")
        else:
            self.write("no")

    def post(self, instance_id=None, action=None):
        return self.rest_handler.post(instance_id=instance_id, action=action)

    def put(self, instance_id):
        return self.rest_handler.put(instance_id=instance_id)

    def delete(self, instance_id):
        return self.rest_handler.delete(instance_id=instance_id)


#class MyRestHandler(cyclone.web.RequestHandler, python_rest_handler.RestRequestHandler):
#    data_manager = MongoDBDataManager


if __name__ == "__main__":
    handlers = [
        (r"/jobs/?", CycloneRestHandler),
        (r"/jobs/([A-Za-z0-9]+)/?", CycloneRestHandler),
        (r"/jobs/([A-Za-z0-9]+)/edit/?", CycloneRestHandler)
        #(r"/jobs/?", CycloneRestHandler)
    ]
    application = cyclone.web.Application(handlers)

    log.startLogging(sys.stdout)
    reactor.listenTCP(8888, application, interface="127.0.0.1")
    reactor.run()
