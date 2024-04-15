import re
from typing import List, Tuple, Union

from core.exceptions.sof import ProcessoForadoPadrao
from config import PROC_REGEX_PATT


class ParseProcNum:

    proc_patt = PROC_REGEX_PATT

    def __parse(self, proc_string:str)->List[Tuple[str]]:

        return re.findall(self.proc_patt, proc_string)
    
    def __extract_from_regex(self, parsed_response:List[Tuple[str]])->List[str]:

        parsed = []

        for tupla in parsed_response:
            for item in tupla:
                if item != '':
                    parsed.append(item)

        return parsed


    def __assert_processo_clean(self, proc_original:str, proc_limpo:str)->None:

        try:
            int(proc_limpo)
        except ValueError as e:
            if 'invalid literal for int' in str(e):
                raise ProcessoForadoPadrao(f'Erro: processo fora do Padrão. Original: {proc_original}. Limpo: {proc_limpo}')
            else:
                raise e
                
    def __clean_processo(self, proc_num:Union[str, int])->str:

        proc = str(proc_num)
        remove = ('.', '/', '-')

        for char in remove:
            proc = proc.replace(char, '')
        
        self.__assert_processo_clean(proc_num, proc)
        return proc
    
    def __check_qtd_procs(self, parsed_clean:list, proc_str:str)->None:

        if len(parsed_clean) < 1:
            raise ProcessoForadoPadrao(f'Nenhum processo no formato encontrado. Valor original: {proc_str}')
        if len(parsed_clean>1):
            raise ProcessoForadoPadrao(f'Foi encontrado mais de um processo. Processos encontrados: {parsed_clean}')


    def __pipeline(self, proc_str:str)->List[str]:

        proc_str = str(proc_str)
        parsed_raw = self.__parse(proc_str)
        extracted = self.__extract_from_regex(parsed_raw)

        parsed_clean = [self.__clean_processo(proc) for proc in extracted]
        self.__check_qtd_procs(parsed_clean, proc_str)

        return parsed_clean
    

    def __call__(self, proc_str:str)->List[str]:

        return self.__pipeline(proc_str)