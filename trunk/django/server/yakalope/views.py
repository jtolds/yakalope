import sys
from django.conf import settings
sys.path.append(settings.LOGMODULE_PATH)
from django.shortcuts import HttpResponse
from models import ServerStatus
from models import Users
from django.utils import simplejson
import logmodule

#Logs in the user
"""
DATA: username=XXXXX&password=XXXXX
returns Status object on success, type=success, message="", data=null
returns Status object on failure, type=failure, message=description, data=null
"""
def login(request):
    c_user = request.GET.get('username','')
    c_pass = request.GET.get('password','')

    valid_login = False
    if c_user and c_pass:
        qset = Users.objects.filter(username=c_user,password=c_pass)
        if len(qset) == 1:
            valid_login = True

    if valid_login:
        request.session['username'] = c_user
        response = ServerStatus("success","",None);
    else:
        try:
            del request.session['username']
        except KeyError:
            pass
        message = "Invalid username or password"
        response = ServerStatus("failure",message,None);

    return HttpResponse(convertToJSON(response), mimetype="text/plain")



#Performs a search of a user's logged messages
"""
DATA: searchterm=XXXXXXXX
returns Status object on success, type=success, message="",
        data=Array of Conversation Objects
returns Status object on failure, type=failure, message=description, data=null
"""
def search(request):
    try:
        username = request.session['username'] \
                 + "@" + settings.LOGMODULE_HOSTNAME
        c_query = request.GET.get('searchterm','')
        if c_query:
            logmod = logmodule.LogModule()
            dp_ok = logmod.setDataDirectory(settings.LOGMODULE_DATA_PATH)
            ip_ok = logmod.setIndexDirectory(settings.LOGMODULE_INDEX_PATH)

            if dp_ok and ip_ok:
                search_cons = logmod.searchMessages(username,c_query)
                if search_cons == False:
                    message = "No logged conversations"
                    response = ServerStatus("success",message,[]);
                else:
                    response = ServerStatus("success","",search_cons)
            else:
                message = "Log path settings are invalid"
                response = ServerStatus("failure",message,None);
        else:
            message = "Empty query"
            response = ServerStatus("failure",message,None);
    except KeyError:
        message = "Not logged in"
        response = ServerStatus("failure",message,None);

    return HttpResponse(convertToJSON(response), mimetype="text/plain")



#Gathers recent messages from the user's logged messages
"""
returns Status object on success, type=success, message="",
        data=Array of Conversation Objects
returns Status object on failure, type=failure, message=description, data=null
"""
def recent(request):
    try:
        username = request.session['username'] \
                 + "@" + settings.LOGMODULE_HOSTNAME

        logmod = logmodule.LogModule()
        dp_ok = logmod.setDataDirectory(settings.LOGMODULE_DATA_PATH)
        ip_ok = logmod.setIndexDirectory(settings.LOGMODULE_INDEX_PATH)

        if dp_ok and ip_ok:
            recent_cons = logmod.getRecentConversations(username)
            if recent_cons == False:
                message = "No logged conversations"
                response = ServerStatus("success",message,[]);
            else:
                response = ServerStatus("success","",recent_cons)
        else:
            message = "Log path settings are invalid"
            response = ServerStatus("failure",message,None);
    except KeyError:
        message = "Not logged in"
        response = ServerStatus("failure",message,None);

    return HttpResponse(convertToJSON(response), mimetype="text/plain")



#Logs the user out of the system, clearing the session
"""
returns Status object ALWAYS, type=success, message="", data=null
"""
def logout(request):
    try:
        del request.session['username']
    except KeyError:
        pass
    response = ServerStatus("success","",None);
    return HttpResponse(convertToJSON(response), mimetype="text/plain")





#Converts the following to JSON:
#  ServerStatus object with the following possible "data" values:
#    None
#    Array of logmodule.LogConversation objects
def convertToJSON(obj):
    if isinstance(obj, ServerStatus):
        if obj.data != None:
            data_dict = []
            for convo in obj.data:
                if isinstance(convo, logmodule.LogConversation):
                    con_dict = convo.toDict()
                    data_dict.append(con_dict);
                else:
                    return "(INVALID JSON CONVERSION: " + \
                           "Expected LogConversation object)"
        else:
            data_dict = None


        obj_dict = {"type": obj.type,
                    "message": obj.message,
                    "data": data_dict}
        return '{"ServerStatus": '+simplejson.dumps(obj_dict)+'}'
    else:
        return "(INVALID JSON CONVERSION: " + \
               "Expected ServerStatus object)"