import tornado.web
import tornado.escape
import json
import werkzeug.security 
import os
from {{appname}}.conf.config import myapp 
from {{appname}}.handlers.base import BaseHandler
from {{appname}}.handlers.powhandlermixin import PowHandlerMixin

class PowHandler(BaseHandler, PowHandlerMixin):
    """
        The Base PowHandler 
        Place to put common stuff for all standard handlers 
        which will remain unaffected by any PoW Changes.
        Purely and only User or Extension controlled.
    """
    
    def get_post_file(self, form_field_name ):
        """ 
            gets the file info from a POSTed html form.
            param: name of the 
        """
        # [{'filename': 'test.mp3', 'body': b'Nur ein Test', 'content_type': 'audio/mpeg'}]
        file_info = self.request.files['file'][0]
        original_fname = file1['filename']
        fname, extension = os.path.splitext(original_fname)
        file_info["extension"] = extension
        file_info["fname"] = fname
        sec_filename = secure_filename(original_fname)
        file_info["secure_filename"] = sec_filename
        file_info["secure_upload_path"]= os.path.join(myapp["upload_path"],sec_filename )
        return file_info

    def success(self, **kwargs):
        """ 
            just adding a user object to every success call
        """
        # add your modifications below.
        # add arguements that are needed by all viwes etc ..
        BaseHandler.success(self, **kwargs)