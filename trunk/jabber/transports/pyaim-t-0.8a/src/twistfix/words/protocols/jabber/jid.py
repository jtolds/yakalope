# -*- test-case-name: twisted.test.test_jabberjid -*-
#
# Twisted, the Framework of Your Internet
# Copyright (C) 2001 Matthew W. Lefkowitz
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from twisted.internet import reactor, protocol, defer
from twisted.words.xish import domish
from twisted.words.protocols.jabber.xmpp_stringprep import nodeprep, resourceprep, nameprep

class InvalidFormat(Exception):
    pass

def parse(jidstring):
    user = None
    server = None
    resource = None

    # Search for delimiters
    user_sep = jidstring.find("@")
    res_sep  = jidstring.find("/")

    if user_sep == -1:        
        if res_sep == -1:
            # host
            server = jidstring
        else:
            # host/resource
            server = jidstring[0:res_sep]
            resource = jidstring[res_sep + 1:] or None
    else:
        if res_sep == -1:
            # user@host
            user = jidstring[0:user_sep] or None
            server = jidstring[user_sep + 1:]
        else:
            if user_sep < res_sep:
                # user@host/resource
                user = jidstring[0:user_sep] or None
                server = jidstring[user_sep + 1:user_sep + (res_sep - user_sep)]
                resource = jidstring[res_sep + 1:] or None
            else:
                # server/resource (with an @ in resource)
                server = jidstring[0:res_sep]
                resource = jidstring[res_sep + 1:] or None

    # Return the tuple
    return prep(user, server, resource)


def prep(user, server, resource):
    """ Stringprep, backported from Twisted 2.0 """

    if user:
        try:
            user = nodeprep.prepare(unicode(user))
        except UnicodeError:
            raise InvalidFormat, "Invalid character in username"
    else:
        user = None

    if not server:
        raise InvalidFormat, "Server address required."
    else:
        try:
            server = nameprep.prepare(unicode(server))
        except UnicodeError:
            raise InvalidFormat, "Invalid character in resource"

    if resource:
        try:
            resource = resourceprep.prepare(unicode(resource))
        except UnicodeError:
            raise InvalidFormat, "Invalid character in resource"
    else:
        resource = None

    return (user, server, resource)



__internJIDs = {}

def intern(str):
    # XXX: Ensure that stringprep'd jids map to same JID
    if str in __internJIDs:
        return __internJIDs[str]
    else:
        j = JID(str)
        __internJIDs[str] = j
        return j

class JID:
    def __init__(self, str = None, tuple = None):
        assert (str or tuple)
        
        if str:
            user, host, res = parse(str)
        else:
            user, host, res = tuple

        self.host = host
        self.user = user
        self.resource = res
            
    def userhost(self):
        if self.user:
            return "%s@%s" % (self.user, self.host)
        else:
            return self.host

    def userhostJID(self):
        if self.resource:
            if "_uhjid" not in self.__dict__:
                self._uhjid = intern(self.userhost())
            return self._uhjid
        else:
            return self

    def full(self):
        if self.user:
            if self.resource:
                return "%s@%s/%s" % (self.user, self.host, self.resource)
            else:
                return "%s@%s" % (self.user, self.host)
        else:
            if self.resource:
                return "%s/%s" % (self.host, self.resource)
            else:
                return self.host

    def __eq__(self, other):
        return (self.user == other.user and
                self.host == other.host and
                self.resource == other.resource)

    def __ne__(self, other):
        return not (self.user == other.user and
                    self.host == other.host and
                    self.resource == other.resource)
