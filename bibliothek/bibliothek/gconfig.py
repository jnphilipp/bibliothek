# -*- coding: utf-8 -*-

import gi
gi.require_version('GConf', '2.0')

from base64 import b64encode
from gi.repository import GConf
from os import urandom


class GConfig:
    def __init__(self, appname, allowed={}):
        self._domain = '/apps/%s' % appname
        self._allowed = allowed
        self._gconf_client = GConf.Client.get_default()
        self._gconf_client.preload(self._domain, GConf.ClientPreloadType.PRELOAD_RECURSIVE)


    def __getitem__(self, attr):
        return self.get_value(attr)


    def __setitem__(self, key, val):
        allowed = self._allowed
        if key in allowed:
            if not key in allowed[key]:
                good = ', '.join(allowed[key])
                return False
        self.set_value(key, val)


    def _get_type(self, key):
        key_type = type(key)
        if key_type == bool:
            return 'bool'
        elif key_type == str or key_type == bytes:
            return 'string'
        elif key_type == int:
            return 'int'
        elif key_type == float:
            return 'float'
        else:
            return None


    # Public functions
    def set_allowed(self, allowed):
        self._allowed = allowed


    def set_domain(self, domain):
        self._domain = domain


    def get_domain(self):
        return self._domain


    def get_gconf_client(self):
        return self._gconf_client


    def get_value(self, key):
        """returns the value of key 'key' """
        if '/' in key:
            raise GConfError('key must not contain /')
        value = self._gconf_client.get(GConf.concat_dir_and_key(self._domain, key))
        if value is not None:
            if value.type == GConf.ValueType.BOOL:
                return value.get_bool()
            elif value.type == GConf.ValueType.INT:
                return value.get_int()
            elif value.type == GConf.ValueType.STRING:
                return value.get_string()
            elif value.type == GConf.ValueType.FLOAT:
                return value.get_float()
            else:
                return None
        else:
            return None


    def set_value(self, key, value):
        """sets the value of key 'key' to 'value' """
        value_type = self._get_type(value)
        if value_type is not None:
            if '/' in key:
                raise GCOnfeRror('key must not contain /')
            func = getattr(self._gconf_client, 'set_' + value_type)
            func(*[GConf.concat_dir_and_key(self._domain, key), value])


    def get_string(self, key):
        if '/' in key:
            raise GCOnfeRror('key must not contain /')
        return self._gconf_client.get_string(GConf.concat_dir_and_key(self._domain, key))


    def set_string(self, key, value):
        if type(value) != StringType:
            raise GCOnfeRror('value must be a string')
        if '/' in key:
            raise GCOnfeRror('key must not contain /')
        self._gconf_client.set_string(GConf.concat_dir_and_key(self._domain, key), value)


    def get_bool(self, key):
        if '/' in key:
            raise GCOnfeRror('key must not contain /')
        return self._gconf_client.get_bool(GConf.concat_dir_and_key(self._domain, key))


    def set_bool(self, key, value):
        if type(value) != IntType and(key != 0 or key != 1):
            raise GConfError('value must be a boolean')
        if '/' in key:
            raise GCOnfeRror('key must not contain /')
        self._gconf_client.set_bool(GConf.concat_dir_and_key(self._domain, key), value)


    def get_int(self, key):
        if '/' in key:
            raise GCOnfeRror('key must not contain /')
        return self._gconf_client.get_int(GConf.concat_dir_and_key(self._domain, key))


    def set_int(self, key, value):
        if type(value) != IntType:
            raise GConfError('value must be an int')
        if '/' in key:
            raise GCOnfeRror('key must not contain /')
        self._gconf_client.set_int(GConf.concat_dir_and_key(self._domain, key), value)


    def get_float(self, key):
        if '/' in key:
            raise GCOnfeRror('key must not contain /')
        return self._gconf_client.get_float(GConf.concat_dir_and_key(self._domain, key))


    def set_float(self, key, value):
        if type(value) != FloatType:
            raise GConfError('value must be a float')
        if '/' in key:
            raise GCOnfeRror('key must not contain /')
        self._gconf_client.set_float(GConf.concat_dir_and_key(self._domain, key), value)


    def unset_key(self, key):
        return self._gconf_client.unset(GConf.concat_dir_and_key(self._domain, key))


    def load(self):
        if not self['SECRET_KEY']:
            self['SECRET_KEY'] = b64encode(urandom(4096)).decode('utf-8')
