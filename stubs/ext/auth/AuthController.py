#
#
# DO NOT EDIT THIS FILE.
# This file was autogenerated by python_on_wheels.
# Any manual edits may be overwritten without notification.
#
# 

# date created:     2011-06-21

import sys
import os
from mako.template import Template
from mako.lookup import TemplateLookup
import datetime

sys.path.append( os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), "../lib" )))
sys.path.append( os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), "../models" )))
sys.path.append( os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), "../models/powmodels" )))


import powlib
import BaseController
import datetime


class AuthController(BaseController.BaseController):
    
    def __init__(self):
        self.modelname = "User"
        BaseController.BaseController.__init__(self)
        self.login_required = []
        self.locked_actions = {}
    
    def authenticate(self):
        print "AuthController.authenticate()"
        return
        
    def register(self, powdict):
        """ registers a User """
        self.model.__init__()
        return self.render(model=self.model, powdict=powdict)
    
    def unregister(self, powdict):
        """ unregisters a User """
        self.model.__init__()
        return self.render(model=self.model, powdict=powdict)
    
    def test_render(self, powdict):
        self.model.__init__()
        return self.render_message("Test", "success", powdict=powdict)
    
    def login( self, powdict):
        """ shows the Auth_login.tmpl template form """
        self.model.__init__()
        return self.render(model=self.model, powdict=powdict)
    
    def do_login( self, powdict ):
        """ The real login action """
        user = User.User()
        session = powdict["SESSION"]
        if powdict["REQ_PARAMETERS"].has_key("loginname") and powdict["REQ_PARAMETERS"].has_key("password"):
            try:
                user = user.find_by("loginname",powdict["REQ_PARAMETERS"]["loginname"])
                if user.password == powdict["REQ_PARAMETERS"]["password"]:
                    #login ok
                    session["user.id"] = user.id
                    session["user.loginname"] = user.loginname
                    session.save()
                    powdict["FLASHTEXT"] = "You successfully logged in, %s " % (user.loginname)
                    powdict["FLASHTYPE"] = "success"
                    return self.redirect("welcome",powdict=powdict)
                else:
                    powdict["FLASHTEXT"] = "Error logging you in, %s " % (user.loginname)
                    powdict["FLASHTYPE"] = "error"
                    return self.redirect("login",powdict=powdict)
            except:
                powdict["FLASHTEXT"] = "Error logging you in " 
                powdict["FLASHTYPE"] = "error"
                return self.redirect("login", powdict=powdict)
        else:
            powdict["FLASHTEXT"] = "Error logging you in. You have to fill in username and password. " 
            powdict["FLASHTYPE"] = "error"
            return self.redirect("login", powdict=powdict)
        return
    
    def logout( self, powdict):
        """logs a user out """
        session = powdict["SESSION"]
        session["user.id"] = 0
        session.save()
        powdict["FLASHTEXT"] = "You successfully logged out. " 
        powdict["FLASHTYPE"] = "success"
        return self.redirect("login", powdict=powdict)
    
    def access_granted(self,**kwargs):
        """ 
            returns true if access is ok, meaning that:
            no login required or login required AND user already lgged in.
        """
        powdict = kwargs.get("powdict",None)
        session = powdict["SESSION"]
        is_logged_in = False
        if self.current_action in self.login_required:
            # login required, so check if user is logged in. 
            try:
                if session["user.id"] != 0:
                    return True
            except KeyError:
                    return False
       
        else:
            # no login required
            return True
        # by default return False
        return False
    
