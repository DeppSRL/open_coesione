"""
http://www.sprklab.com/notes/13-passing-arguments-to-functions-in-django-template

we can pass the arguments to getPrice by writing
`` {{ meeting|args:user|call:"getPrice" }}.

So we set the arguments using "args" and then call the function using "call".
To call multiple arguments do
`` {{ meeting|args:arg1|args:arg2|call:"getPrice" }}.

"""
from django.template import Library

register = Library()

def callMethod(obj, methodName):
    method = getattr(obj, methodName)

    if obj.__dict__.has_key("__callArg"):
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()

def args(obj, arg):
    if not obj.__dict__.has_key("__callArg"):
        obj.__callArg = []

    obj.__callArg += [arg]
    return obj

register.filter("call", callMethod)
register.filter("args", args)