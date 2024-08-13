from pandas import DataFrame, Series
import re

from core.exceptions.xl import ColunaDadosNaoEncontrada
from core.utils.str import remover_acentos
from core.parsers import parse_proc_num

from config import COL_PROC_REGEX_PATT, SUCCESS

COL_STATUS_PROC_PARSE='status_parseamento_processo'
COL_PARSED_PROC='processo_extraido'

class GetProcNum:

    def __init__(self, verbose=True)->None:

        self.__parse_proc = parse_proc_num
        self.verbose = verbose

    def __create_cols_proc(self, df:DataFrame)->DataFrame:

        df = df.copy()
        df[COL_STATUS_PROC_PARSE]=''
        df[COL_PARSED_PROC]=''

        return df
    
    def __clean_col(self, col:str)->str:

        col = str(col)
        col = col.lower().rstrip().lstrip()
        col = remover_acentos(col)

        return col

    def __find_col(self, pattern:str, df:DataFrame)->str:
        '''Returns first match'''

        for col in df.columns:
            col_clean = self.__clean_col(col)
            if re.search(pattern, col_clean):
                return col
        else:
            raise ColunaDadosNaoEncontrada(f'Padrao: {pattern}. Colunas: {df.columns}')

    def __parse_proc_row(self, i:int, row:Series, df:DataFrame, col_processo:str)->None:

        try:
            proc_str = row[col_processo]
            parsed_proc = self.__parse_proc(proc_str)
            df.loc[i, COL_PARSED_PROC]=parsed_proc
            df.loc[i, COL_STATUS_PROC_PARSE]=SUCCESS
        except Exception as e:
            df.loc[i, COL_PARSED_PROC]=None
            df.loc[i, COL_STATUS_PROC_PARSE]=f'Erro: {str(type(e).__name__)} - {str(e)}'

    def __parse_procs(self, df:DataFrame)->None:

        
        col_processo = self.__find_col(COL_PROC_REGEX_PATT, df)

        for i, row in df.iterrows():
            self.__parse_proc_row(i, row, df, col_processo)
        
        return df

    def __pipeline_parse_proc(self, df:DataFrame)->DataFrame:

        df = df.copy()
        df = self.__create_cols_proc(df)

        return self.__parse_procs(df)
    
    def __print_sucess_rate(self, df:DataFrame)->None:

        if self.verbose:
            sucesso = df[COL_STATUS_PROC_PARSE]==SUCCESS
            rate = round(sucesso.mean(), 3)
            print(f'Taxa de sucesso no parseamento do processo: {rate*100}%')


    def __call__(self, df:DataFrame)->DataFrame:

        df = self.__pipeline_parse_proc(df)
        self.__print_sucess_rate(df)

        return df

