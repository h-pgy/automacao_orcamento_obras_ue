from .client.rest_client import RestClient

from core.utils.date import is_current_year, current_month
from core.utils.misc import list_envelope
from core.exceptions.sof import RespError, EmpenhoInexistente

from config import SOF_API_HOST, SOF_API_TOKEN, SOF_API_VERSION

from typing import List

#mes padrao é dezembro pois sof é cumulativo
MES_PADRAO=12

class EmpenhosApiSof:

    version = SOF_API_VERSION

    def __init__(self):

        self.client = RestClient(SOF_API_HOST, SOF_API_TOKEN)

    @list_envelope
    def __get_empenhos_by_proc(self, num_proc:int, mes:int, ano:int)->List[dict]:

        api_resp = self.client.get(self.version, 
                                   endpoint='empenhos', 
                                   anoEmpenho=ano, 
                                   mesEmpenho=mes,
                                   numProcesso=num_proc
                                   )
        status = api_resp['metadados']['txtStatus']
        if status!='OK':
            raise RespError(f'Erro na resposta da API do SOF: {status}')
        
        return api_resp['lstEmpenhos']
    
    def __solve_month(self, ano:int)->List[dict]:

        if is_current_year(ano):
            return current_month()
        return MES_PADRAO
    

    def __get_empenho_ano(self, num_proc:int, ano:int)->List[dict]:

        mes = self.__solve_month(ano)

        resp = self.__get_empenhos_by_proc(num_proc, mes, ano)
        if resp is None or len(resp)<1:
            raise EmpenhoInexistente(f'Não há empenhos para o proc {num_proc} em {mes}/{ano}')
        return resp
    
    def __call__(self, num_proc:int, ano:int)->List[dict]:

        return self.__get_empenho_ano(num_proc, ano)