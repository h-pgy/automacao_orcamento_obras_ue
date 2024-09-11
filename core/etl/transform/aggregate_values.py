import pandas as pd
import re
from typing import List

REGEX_COL_EMPENHO = r'^empenho_liquido_\d{4}$'
REGEX_COL_LIQUIDADO = r'^valor_liquidado_\d{4}$'

class Agregator:

    def __init__(self, verbose:bool=True):

        self.verbose = verbose

    def __agregar_sum(self, df:pd.DataFrame, columns:List[str], fillna:bool=True)->pd.Series:

        if fillna:
            df = df[columns].fillna(0)

        valores_agregados = df[columns].sum(axis=1)

        return valores_agregados
    
    def somar_empenho(self, df:pd.DataFrame)->pd.DataFrame:

        if self.verbose:
            print('Agregando colunas de empenho')

        df = df.copy()
        cols_empenho = [col for col in df.columns if re.match(REGEX_COL_EMPENHO, col)]
        for col in cols_empenho:
            df[col] =  pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['empenho_total'] = self.__agregar_sum(df, cols_empenho)

        return df
    
    def somar_liquidado(self, df:pd.DataFrame)->pd.DataFrame:

        if self.verbose:
            print('Agregando colunas de liquidação')

        df = df.copy()
        cols_liquidado = [col for col in df.columns if re.match(REGEX_COL_LIQUIDADO, col)]
        for col in cols_liquidado:
            df[col] =  pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['valor_liquidado_total'] = self.__agregar_sum(df, cols_liquidado)

        return df
    