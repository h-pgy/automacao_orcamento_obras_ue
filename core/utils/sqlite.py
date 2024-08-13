import sqlite3
from sqlite3 import Error, Connection, Cursor
from typing import List
import os
from .str import check_alphanum, check_ascii


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        yield conn
    except Error as e:
        print(f"{type(e).__name__} : {e}")
    finally:
        if conn:
            conn.close()

class SingleSqliteClient:


    allowed_data_types = {
        'INTEGER',
        'TEXT',
        'BLOB',
        'REAL',
        'NUMERIC'
    }

    def __init__(self, db_file:str, create=True)->None:
        '''Simple sqlite client'''

        if not db_file.endswith('.sqlite'):
            raise ValueError('DB file must be .sqlite extension')
        self.db_file = db_file            
        self.__solve_db_creation(create)

    def __solve_db_creation(self, create:bool):
        
        if not self.__check_db_exists(self.db_file):
            if not create:
                raise ValueError(f'DB file does not exist. Must set create to True if you want to create a new one.')
            self.__create_conn(self.db_file)

    def __check_db_exists(self, db_file:str)->bool:
         
         return os.path.exists(db_file) and os.path.isfile(db_file) and db_file.endswith('.sqlite')
    
    def __check_column_type(self, type:str)->None:

        if str(type).upper().strip() not in self.allowed_data_types:
                raise ValueError(f'Type {type} not allowed. Allowed: {self.allowed_data_types}')
        
    def __check_column_name(self, name:str)->None:
         
        if type(name) is not str:
            raise ValueError(f'Col names must be str. Error in col {name}')
        if not check_ascii(name):
            raise  ValueError(f'Col names must be ascii. Error in col {name}')
        
        if not check_alphanum(name):
            raise  ValueError(f'Col names must be alphanumeric. Error in col {name}')
    
    def __check_columns_dict(self, columns:dict)->None:

        for key, val in columns.items():

            self.__check_column_name(key)
            self.__check_column_type(val)

    def __create_conn(self, db_file:str)->Connection:

        conn_gen = create_connection(db_file)

        return next(conn_gen)
    
    def __execute_query(self, conn:Connection, query:str)->None:

        c = None
        try:
            c = conn.cursor()
            c.execute(query)
            conn.commit()
            c.close()
        except Error as e:
            print(f"{type(e).__name__} : {e}")
        finally:
            if c:
                c.close()

    def __column_config(self, column_name:str, type:str, pkey:str, not_nulls:List[str], uniques:List[str])->str:

        statement = f'{column_name} {type}'
        if column_name == pkey:
            statement += ' PRIMARY KEY'
        if column_name in not_nulls:
            statement += ' NOT NULL'
        if column_name in uniques:
            statement += ' UNIQUE'
        
        return statement


    def __create_db_query(self, columns:dict, pkey:str=None, not_nulls:List[str]=None, uniques:List[str]=None)->str:

        self.__check_columns_dict(columns)
        columns = ',\n'.join([self.__column_config(col_name, type, pkey, not_nulls, uniques)
                               for col_name, type in columns.items()])

        query=f'''CREATE TABLE IF NOT EXISTS tasks (
            id integer PRIMARY KEY,
            {columns}
        );'''

        self.__execute_query(query)


    def __create_table(self, db_file:str, columns:dict)->None:
        
        conn = self.__create_conn(db_file)
        self.__create_db_query(conn, columns)

    

