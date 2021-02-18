import tornado.ioloop
import tornado.web
from {{appname}}.handlers.powhandler import PowHandler
from {{appname}}.lib.application import app, route

# ROUTING:
# You can decorate routes on the handler classes or on the methods directly.
# 
# You can use flask/werkzeug style routing.
#      example: @app.add_route('/test/<uuid:identifier>', dispatch={"get" : "testuuid"})
# Or you can use regex in the routes as well:
#      example: @route('/test/([0-9]+)', dispatch=["get"] )
#      any regex goes. any group () will be handed to the handler 
#      see example handler below.
# 
# Check the docs for more info: https://www.pythononwheels.org/documentation
#

@app.add_route(r"/", dispatch={"get" : "index"}, pos=1)
#@app.add_route(r"/index/([0-9]+)", dispatch={"get" : "index_identifier", "params" : ["identifier"] })
@app.make_routes()
class IndexdHandler(PowHandler):
    def index(self, year=None):
        """
            Example Method with class attached routing (see above "/" )
        """
        print(" Calling IndexHandler.index from handlers/shorties.py: parameter index: " + str(year))
        self.render("index.tmpl")
    
    @route(r'/index/<uuid:identifier>', dispatch=["get"])
    def index_uuid(self, identifier=None):
        """
            Example method with Method attached route and Flask style route
        """
        print(" Calling Indexhandler.tetuuid Indentifier: {}".format(str(identifier)))
        self.write("uuid: " + str(identifier))
    
    @route(r"/index/([0-9]+)", dispatch=["get"], params=["identifier"])
    def index_identifier(self, identifier=None):
        """
            Example method with Method attached route and tornado/regex style route
        """
        print(" Calling Indexhandler.get_story Indentifier: {}".format(str(identifier)))
        self.write("int: " + str(identifier))

@app.make_routes()
class PyTestHandler(PowHandler):
    @route(r"/testresults", dispatch=["get"])
    def show_results(self):
        """
            this action will show the pytest from test/runtests.py 
        """
        self.render("testreport.html")
    
    @route(r"/versiontest", dispatch=["get"])
    def show_results(self):
        """
            this action will show the pytest from test/runtests.py 
        """
        self.render("versiontest.html")
    
    @route(r'/test/<uuid:identifier>', dispatch=["get"])
    def testuuid(self, identifier=None):
        """
            Example method with Method attached route and Flask style route
        """
        print(" Calling Indexhandler.tetuuid Indentifier: {}, format: {}".format(str(identifier)))
        self.render("index.tmpl")
    
    @route(r'/test/<int:id>', dispatch=["get"])
    def testuuid2(self, id=None):
        """
            Testcase: dont delete (see tests/run_tests.py)
        """
        self.write("12")
    
# this will be the last route since it has the lowest pos.
@app.make_routes()
class ErrorHandler(PowHandler):
    @route(r".*", dispatch=["get", "post", "put", "delete"], pos=0)
    def handle_all(self):
        self.error( 
            template="404.tmpl", 
            http_status=404,
            data={ 
                "next"      : None,
                "prev"      : self.request.headers.get("Referer"),
                "message"   : "URL not found error"
                }, 
            message="URL not found error",
            referer=self.request.headers.get("Referer")
        )


# @app.add_route('/image/upload', dispatch={"post" : "upload"})
# class ImageUploadSample(PowHandler):
#     #
#     # Sample file upload handler
#     #
#     def upload(self, testval=0):
#         """
#             handle image uploads
#         """ 
#         for field_name, files in self.request.files.items():
#             print(field_name)

#         print(str(self.request.files))
#         file_info = self.get_post_file()
#         print(str(file_info))