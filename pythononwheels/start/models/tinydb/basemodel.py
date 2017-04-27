from tinydb import TinyDB, Query, where
from {{appname}}.powlib import pluralize
import datetime
from cerberus import Validator
import xmltodict
import simplejson as json
import datetime, decimal
from {{appname}}.config import myapp
from {{appname}}.database.tinydblib import tinydb
from {{appname}}.powlib import merge_two_dicts
from {{appname}}.models.modelobject import ModelObject
import uuid
from {{appname}}.encoders import pow_json_serializer

#print ('importing module %s' % __name__)
class TinyBaseModel(ModelObject):
    
    basic_schema = {
        "id"    :   { "type" : "string" },
        #"eid"   :   { "type" : "string" },
        "created_at"    : { "type" : "datetime" },
        "last_updated"    : { "type" : "datetime" },
    }
    
    where=where
    Query=Query()

    def init_on_load(self, *args, **kwargs):
        
        #self.id = uuid.uuid4()
        #self.created_at = datetime.datetime.now()
        #self.last_updated = datetime.datetime.now()

        self.session=None
        self.tablename = pluralize(self.__class__.__name__.lower())
        #
        # all further Db operations will work on the table
        #
        self.table = tinydb.table(self.tablename)
        self.where = where

        #
        # if there is a schema (cerberus) set it in the instance
        #
        if "schema" in self.__class__.__dict__:
            #print(" .. found a schema for: " +str(self.__class__.__name__) + " in class dict")
            self.schema = merge_two_dicts(
                self.__class__.__dict__["schema"],
                self.__class__.basic_schema)
            #print("  .. Schema is now: " + str(self.schema))

        # setup  the instance attributes from schema
        for key in self.schema.keys():
            if self.schema[key].get("default", None) != None:
                setattr(self,key,self.schema[key].get("default"))
                self.schema[key].pop("default", None)
            else:
                #print("no default for: " + str(self.schema[key]))
                setattr(self, key, None)
                    
        #
        # setup values from kwargs or from init_from_<format> if format="someformat"
        # example: m = Model( data = { 'test' : 1 }, format="json")
        # will call m.init_from_json(data)
        #
        if "format" in kwargs:
            # set the format and call the according init_from_<format> method
            # which initializes the instance with the given vaules (from data)
            # e.g. Model(format=json, data={data})
            f = getattr(self, "init_from_" + kwargs["format"], None)
            if f:
                f(kwargs)
        else:
            # initializes the instanmce with the given kwargs values:
            # e.g.: Model(test="sometext", title="sometitle")
            for key in kwargs.keys():
                #if key in self.__class__.__dict__:
                if key in self.schema:
                    setattr(self, key, kwargs[key])


    def json_load_from_db(self, data, keep_id=False):
        #TODO:  refresh the object from db and return json
        pass

    def print_schema(self):
        print(50*"-")
        print("Schema for: " + str(self.__class__))
        from pprint import PrettyPrinter

    def get_relationships(self):
        """ Method not available for TinyDB Models """
        raise RuntimeError("Method not available for TinyDB Models ")

    def get_relations(self):
        """
            returns a list of the relation names
        """
        raise RuntimeError("Method not available for TinyDB Models ")

    def print_full(self):
        #
        # prints everything including related objects in FULL
        # lenghty but you see everything.
        #
        raise RuntimeError("Method not available for TinyDB Models ")

    def __repr__(self):
        #
        # __repr__ method is what happens when you look at it with the interactive prompt
        # or (unlikely: use the builtin repr() function)
        # usage: at interactive python prompt
        # p=Post()
        # p
        from pprint import pformat
        d = self.to_dict()
        return pformat(d,indent=+4)

    def __str__(self):
        #
        # The __str__ method is what happens when you print the object
        # usage:
        # p=Post()
        # print(p)
        return self.__repr__()
                       
    def create_table(self):
        """
            created the physical table in the DB
        """
        if not self.table:
            self.table = tinydb.table(self.tablename)

    def drop_table(self):
        """
            created the physical table in the DB
        """
        tinydb.purge_table(self.tablename)
    
    def upsert(self):
        """ insert or update intelligently """
        
        #self.created_at = datetime.datetime.now()
        #self.last_updated = datetime.datetime.now()
        if getattr(self, "eid", None):
            # if the instance has an eid its already in the db
            # update
            print("update by eid:" + str(self.eid))
            Q = Query()
            self.last_updated = datetime.datetime.now()
            self.table.update(self.to_dict(),Q.id==self.id)
        else:
            #first check if id is in db:
            Q = Query()
            res=self.table.get(Q.id==self.id)
            if res:
                #update. object is already in db
                print("update by id:" + str(self.id))
                self.last_updated = datetime.datetime.now()
                self.table.update(self.to_dict(),Q.id==self.id)
            else:
                # insert  
                 
                self.last_updated = datetime.datetime.now()
                self.created_at = self.last_updated
                self.id = str(uuid.uuid4())
                self.eid = self.table.insert(self.to_dict())         
                print("insert, new eid: " +str(self.eid))            


    def get_by_eid(self, eid=None):
        """ return by id """
        if not eid:
            eid = self.eid
        Q = Query()
        res = self.table.search(Q.eid == eid)
        return res

    def get_by_id(self, id=None):
        """ return by id """
        if not self.id:
            id = self.id
        Q = Query()
        res = self.table.search(Q.id == str(id))
        return res
        

    def from_statement(self, statement):
        """ Method not available for TinyDB Models """
        raise RuntimeError("Method not available for TinyDB Models ")

    def page(self, *criterion, limit=None, offset=None):
        """ return the next page 
            contains all elements from offset(first element) -> to limit (last element).
        """
        def testfunc(val, start, end ):
            return start <= val <= end
        Q = Query()
        print(str(*criterion))
        Att = getattr(Q, *crtiterion)
        res = self.table.search(Att(testfunc, start, end ))

    def json_result_to_object(self, res):
        """
            creates a list of instances of this model 
            from a given json resultlist
        """
        if not isinstance(res,(list)):
            #single element, pack it in a list
            res = [res]
        # lists, iterate over all elements
        reslist = []
        for elem in res:
            m = self.__class__()
            #print(str(type(elem)) + "->" + str(elem))
            m.init_from_json(json.dumps(elem, default=pow_json_serializer))
            #print("adding model to reslist: " + str(m))
            setattr(m,"eid", elem.get("eid", None))
            reslist.append(m)
        return reslist
    
    # def res_to_json(self, res):
    #     """
    #         returns a list of results in a json serialized format.
    #     """
    #     return json.loads(json.dumps(res, default=pow_json_serializer))
    def _return_find(self, res, as_json=True):
        """
            _return_find gives the right result.
            either as json
            or as object (Model Class / Instance)
        """
        reslist = self.json_result_to_object(res)
        if as_json:
            return self.res_to_json(reslist)
        else:
            return reslist

    def find(self,*criterion, as_json=False):
        """ Find something given a query or criterion """
        print("  .. find: " + str(*criterion))
        res = self.table.search(*criterion)
        return self._return_find(res, as_json)
    
    def find_random(self, as_json=False):
        """ Find and return a random element """
        import random
        res = self.table.all() # returns a list of tinyDB DB-Elements
        #print(res)
        randnum = random.randrange(len(res))
        #print(" random: " + str(randnum))
        res=[res[randnum]]
        return self._return_find(res, as_json)

    def find_all(self, as_json=False):
        """ Find something given a query or criterion and parameters """
        res = self.table.all() # returns a list of tinyDB DB-Elements 
        return self._return_find(res, as_json)
    
    def find_one(self, *criterion, as_json=False):
        """ find only one result. Raise Excaption if more than one was found"""
        print("criterion: " + str(criterion))
        try:
            res = self.table.get(*criterion)
            return self._return_find(res, as_json)
        except Exception as e:
            raise e

    def find_first(self, *criterion, as_json=False):
        """ return the first hit, or None"""
        return self.find_one(*criterion, as_json=as_json)

    def q(self):
        """ return a raw query """
        # for sqlalchemy: return session.query(self.__class__)
        # for elastic: return  Q
        # for tinyDB return Query
        return Query()
        


