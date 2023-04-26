import threading, json
from transformers import pipeline
import importlib

MODEL_PATH = 'gogamza/kobart-base-v2'
class TextSummarizer :
    __model_path = ''
    __summarizer = ''

    def __init__(self, model_path) -> None:
        self.__model_path = model_path
        self.__summarizer = pipeline('summarization', model= model_path, min_length=64, max_length=128, tokenizer=model_path)
    
    def summarize(self, text) -> str:
        text = text.replace("\n", ' ') #줄바꿈 제거
        text = text.strip() #좌우 공백 제거
        return self.__summarizer(text)[0].get('summary_text')


class MiddleWare :
    __port = 0
    __web_sever_ip = 0
    __web_sever_port = 0
    __db_ip = 0
    __db_port = 0
    __db_id = 0
    __db_pass = 0


    
    def __init__(self, setting_json_path, db_library, port=20000,) -> None : 
        self.__port = port
        with open(setting_json_path, 'r', encoding='utf-8') as js_data :
            datas = json.load(js_data)
            self.__db_id = datas['DB']['ID']
            self.__db_pass = datas['DB']['PASSWORD']
            self.__db_ip = datas['DB']['IP']
            self.__db_port = datas['DB']['PORT']
            self.__web_sever_ip = datas['WEB']['IP']
            self.__web_sever_port = datas['WEB']['PORT']
        db_lib = importlib.import_module(db_library)
        




    