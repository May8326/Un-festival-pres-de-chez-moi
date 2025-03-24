def to_bool(s):
    r = False 
    if(s.lower() == "true"):
        r = True
    elif(s.lower() == "false"):
        r = False
    return r

def clean_arg(arg):
    if arg == "":
        return None
    else:
        return arg