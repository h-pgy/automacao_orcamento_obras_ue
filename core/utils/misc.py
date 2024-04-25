import pandas as pd

def list_envelope(func):

    def wraped(*args, **kwargs):

        resp  = func(*args, **kwargs)

        if (type(resp) is not list) and not pd.isnull(resp):
            resp = [resp]
    
        return resp
    
    return wraped
