import pandas as pd

def list_envelope(func):

    def wraped(*args, **kwargs):

        resp  = func(*args, **kwargs)

        if (type(resp) is not list) and not pd.isnull(resp):
            resp = [resp]
    
        return resp
    
    return wraped


def catch_error_to_str(func):

    def wraped(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f'Erro: {str(type(e).__name__)} - {str(e)}'
    
    return wraped
