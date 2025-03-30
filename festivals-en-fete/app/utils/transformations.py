def to_bool(s:str):
    r = False 
    if(str(s).lower() == "true"):
        r = True
    elif(str(s).lower() == "false"):
        r = False
    return r

def clean_arg(arg):
    if arg == "":
        return None
    else:
        return arg