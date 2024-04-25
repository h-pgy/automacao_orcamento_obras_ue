from typing import Union
import pandas as pd

from core.exceptions.sof import RespDataError
from core.utils.str import read_json_str
from core.utils.misc import catch_error_to_str
from config import ANO_INICIAL, ANO_FINAL

COL_RETORNO_SOF='retorno_sof_{ano}'


class ExtractSofData:

    def __init__(self, verbose:bool=True)->None:

        self.verbose = verbose

    @catch_error_to_str
    def __extract_sof_data(self, sof_data:dict, key:str, numeric:bool=True)->Union[str, float]:

        if sof_data is None:
            raise RespDataError(f'Não há dados para parsear')

        try:
            data = sof_data[key]
        except KeyError:
            raise RespDataError(f'Chave inexistente na resposta do SOF: {key}')
        try:
            if pd.isnull(data):
                return data
            if numeric:
                return float(data)
            else:
                return str(data)
        except Exception as e:
            raise RespDataError(f'Valor do SOF fora do padrão para a chave {key}: {data}')

    def get_empenho_liquido(self, sof_data:dict)->float:

        chave='valEmpenhadoLiquido'
        return self.__extract_sof_data(sof_data, chave, numeric=True)
    
    def get_val_liquidado(self, sof_data:dict)->float:

        chave='valLiquidado'
        return self.__extract_sof_data(sof_data, chave, numeric=True)

    def get_contrato(self, sof_data:dict)->str:

        chave = 'numContrato'
        return self.__extract_sof_data(sof_data, chave, numeric=False)
    
    def get_nota_empenho(self, sof_data:dict)->str:
        
        chave = 'codEmpenho'
        return self.__extract_sof_data(sof_data, chave, numeric=False)
    
    def get_fornecedor(self, sof_data:dict)->str:
        
        chave = 'numCpfCnpj'
        return self.__extract_sof_data(sof_data, chave, numeric=False)
    
    def __concat(self, values:list)->str:

        if values is None:
            return None
        if type(values) is str:
            return values
        #pegando apenas valores unicos
        values = list(set(values))
        return '; '.join(values)

    def __sum(self, values:list)->float:

        try:
            values = [val if val is not None else 0 for val in values]
            return sum(values)
        except TypeError:
            return self.__concat(values)
    
    @catch_error_to_str    
    def __extract(self, extract_method:str, resp:Union[list, None])->Union[str, float, None]:

        extract_func = getattr(self, extract_method)
        if pd.isnull(resp):
            return None
        
        resp  = read_json_str(resp)
        return [extract_func(emp) for emp in resp]
    
    def __build_column(self, df:pd.DataFrame, col_sof_data:pd.Series, col_name:str, extract_method:str, sum:bool)->None:

        if self.verbose:
            print(f'Building column: {col_name}')

        df[col_name] = df[col_sof_data].apply(lambda x: self.__extract(extract_method, x))

        if sum:
            df[col_name]=df[col_name].apply(self.__sum)
        else:
            df[col_name]=df[col_name].apply(self.__concat)

    def __col_empenho(self, df:pd.DataFrame, ano:int)->None:

        col_sof_data = COL_RETORNO_SOF.format(ano=ano)
        metodo = 'get_empenho_liquido'
        col_name = f'empenho_liquido_{ano}'

        self.__build_column(df, col_sof_data, col_name, metodo, sum=True)

    def __col_val_liquidado(self, df:pd.DataFrame, ano:int)->None:

        col_sof_data = COL_RETORNO_SOF.format(ano=ano)
        metodo = 'get_val_liquidado'
        col_name = f'valor_liquidado_{ano}'

        self.__build_column(df, col_sof_data, col_name, metodo, sum=True)

    def __col_contrato(self, df:pd.DataFrame, ano:int)->None:

        col_sof_data = COL_RETORNO_SOF.format(ano=ano)
        metodo = 'get_contrato'
        col_name = f'contrato_{ano}'

        self.__build_column(df, col_sof_data, col_name, metodo, sum=False)

    def __col_nota_empenho(self, df:pd.DataFrame, ano:int)->None:

        col_sof_data = COL_RETORNO_SOF.format(ano=ano)
        metodo = 'get_nota_empenho'
        col_name = f'nota_empenho_{ano}'

        self.__build_column(df, col_sof_data, col_name, metodo, sum=False)

    def __col_fornecedor(self, df:pd.DataFrame, ano:int)->None:

        col_sof_data = COL_RETORNO_SOF.format(ano=ano)
        metodo = 'get_fornecedor'
        col_name = f'fornecedor_{ano}'

        self.__build_column(df, col_sof_data, col_name, metodo, sum=False)

    def __pipeline(self, df:pd.DataFrame)->pd.DataFrame:

        df = df.copy()

        for ano in range(ANO_INICIAL, ANO_FINAL+1):
            self.__col_empenho(df, ano)
            self.__col_val_liquidado(df, ano)
            self.__col_contrato(df, ano)
            self.__col_nota_empenho(df, ano)
            self.__col_fornecedor(df, ano)
        
        return df
    
    def __call__(self, df:pd.DataFrame)->pd.DataFrame:

        return self.__pipeline(df)