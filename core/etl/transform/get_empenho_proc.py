from pandas import DataFrame, Series
import re
from tqdm import tqdm
import json
from typing import List, Union

from core.exceptions.xl import ColunaDadosNaoEncontrada
from core.utils.str import remover_acentos
from core.api import get_empenhos

from config import ANO_INICIAL, ANO_FINAL, SUCCESS

from .get_proc_num import COL_PARSED_PROC, COL_STATUS_PROC_PARSE

COL_STATUS_API_SOF='status_retorno_api_sof_{ano}'
COL_RETORNO_SOF='retorno_sof_{ano}'


ANOS = list(range(ANO_INICIAL, ANO_FINAL+1))

class GetEmpenhoProc:

    def __init__(self, verbose=True)->None:

        self.__get_empenho = get_empenhos
        self.verbose = verbose
        self.anos = ANOS

    def __create_cols_sof(self, df:DataFrame)->DataFrame:

        df = df.copy()
        for ano in self.anos:
            df[COL_STATUS_API_SOF.format(ano=ano)]=''
            df[COL_RETORNO_SOF.format(ano=ano)]=''

        return df

    def __set_row_response(self, df:DataFrame, ano:int, i:int, resp_sof:Union[List[dict], None], msg:str)->None:

        df.loc[i, COL_RETORNO_SOF.format(ano=ano)]=json.dumps(resp_sof)
        df.loc[i, COL_STATUS_API_SOF.format(ano=ano)]=msg

    def __set_row_data(self, row:Series, ano:int, i:int, df:DataFrame)->None:

        if row[COL_STATUS_PROC_PARSE]==SUCCESS:
            proc = row[COL_PARSED_PROC]
            resp_sof = self.__get_empenho(proc, ano)
            self.__set_row_response(df, ano, i, resp_sof, SUCCESS)
        else:
            msg = f'Erro no número do processo'
            self.__set_row_response(df, ano, i, None, msg)

    def __get_empenho_row(self, ano:int, i:int, row:Series, df:DataFrame)->None:

        try:
            self.__set_row_data(row, ano, i, df)
        except Exception as e:
            msg = f'Erro: {str(type(e).__name__)} - {str(e)}'
            self.__set_row_response(df, ano, i, None, msg)

    def __get_empenhos(self, ano:int, df:DataFrame)->None:

        df = df.copy()
        for i, row in tqdm(df.iterrows()):
            self.__get_empenho_row(ano, i, row, df)
        
        return df

    def __pipeline_get_empenho(self, df:DataFrame)->DataFrame:

        df = df.copy()
        df = self.__create_cols_sof(df)

        for ano in self.anos:
            df = self.__get_empenhos(ano, df)

        return df
    
    def __print_sucess_rate(self, df:DataFrame)->None:

        if self.verbose:
            for ano in self.anos:
                sucesso = df[COL_STATUS_API_SOF.format(ano=ano)]==SUCCESS
                rate = round(sucesso.mean(), 3)
                print(f'Taxa de sucesso na busca no SOF para o ano{ano}: {rate*100}%')


    def __call__(self, df:DataFrame)->DataFrame:

        df = self.__pipeline_get_empenho(df)
        self.__print_sucess_rate(df)

        return df
