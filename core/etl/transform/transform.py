import pandas as pd
import os

from typing import Union

from core.utils.io import solve_path
from .get_proc_num import GetProcNum
from .get_empenho_proc import GetEmpenhoProc
from .extract_sof_data import ExtractSofData
from .aggregate_values import Agregator

from config import GENERATED_DATA_DIR

ARQUIVO_INTERMEDIARIO = 'dados_sof.xlsx'

class Transform:

    def __init__(self, verbose:bool=True, save_intermediary_df:bool=True, load_intermediary:bool=True):

        self.verbose = verbose
        self.get_proc_num = GetProcNum(verbose=verbose)
        self.get_empenhos = GetEmpenhoProc(verbose=verbose)
        self.extract_sof_data = ExtractSofData(verbose=verbose)
        self.agregador = Agregator(verbose=verbose)

        self.save_intermediary_df=save_intermediary_df
        self.load_intermediary = load_intermediary

    def __load_intermediary(self)->pd.DataFrame:

        if self.load_intermediary:
            path_intermediary = solve_path(ARQUIVO_INTERMEDIARIO, GENERATED_DATA_DIR)
            if os.path.exists(path_intermediary):
                if self.verbose:
                    print('Loading intermediary dataframe')
                return pd.read_excel(path_intermediary)
        print('Creating new dataframe pulling data from SOF')

    def __intermediary_pipeline(self, df:pd.DataFrame)->pd.DataFrame:

        df = self.get_proc_num(df)
        df = self.get_empenhos(df)
        if self.save_intermediary_df:
            self.__save_df(df, ARQUIVO_INTERMEDIARIO)
        return df
    
    def __solve_intermediary(self, df:pd.DataFrame)->Union[pd.DataFrame, None]:

        df_inter = self.__load_intermediary()
        if df_inter is None:
            df = self.__intermediary_pipeline(df)
            return df
        else:
            return df_inter

    def __save_df(self, df:pd.DataFrame, fname:str)->None:

        fpath = solve_path(fname, GENERATED_DATA_DIR)
        df.to_excel(fpath, index=False)

    def __pipeline(self, df:pd.DataFrame)->pd.DataFrame:

        df = self.__solve_intermediary(df)
        df = self.extract_sof_data(df)
        df = self.agregador.somar_empenho(df)
        df = self.agregador.somar_liquidado(df)

        return df
    
    def __call__(self, df:pd.DataFrame)->pd.DataFrame:

        return self.__pipeline(df)