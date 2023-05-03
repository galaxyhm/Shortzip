from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import uvicorn

app = FastAPI()

def textProcessing( text: str) -> str:
    text = text.replace(u'\n', u' ')
    text = text.replace(u'\'', u' ')
    text = text.replace(u'\\\'', u' ')
    text = text.replace(u'[', u'')
    text = text.replace(u']', u'')
    text = text.replace(u'\xa0', u' ')
    text = text.replace(u'\"', u'')
    text = text.replace(u'\'', u'')
    text = text.replace(u'  ', u' ')
    text = text.replace(u'  ', u' ')
    text = text.replace(u'  ', u' ')

    return text.strip()

class UrlItem(BaseModel):
    url: str


class TextItem(BaseModel):
    text: str


# fast api 시작후 모델 로드및 초기화
class SummarizeModel:
    summarizer = None

    def __init__(self):
        self.summarizer = pipeline("summarization", model="galaxyhm/kobartv2-summarizer-using_data",
                                   tokenizer='galaxyhm/kobartv2-summarizer-using_data')



class BinaryTextClassificationModel:
    classifier = None 

    def __init__(self):
        self.classifier = pipeline( model='daekeun-ml/koelectra-small-v3-nsmc', tokenizer='daekeun-ml/koelectra-small-v3-nsmc')





summarize_model = SummarizeModel()


# 크롤링후 테스트요약
# @app.post("/crawl/naver/")
# async def crawl(url: UrlItem):

#     list_list = NewsCrawler.navercrawl(url.url)
#     if len(list_list) == 7:
#         a, b, c, d, e, f, g = list_list
#     else:
#         a,b,c,d,e,f = list_list


#     text = model.summarizer(d, min_length=32, max_length=len(d) / 2)
#     # print(type(text))
#     # print(text[0])
#     text[0]['summary_text'] = NewsCrawler.textProcessing(text[0]['summary_text'])
#     text.append({'text': d})
#     return {'message': text}


# 입력 글자수 체크 밑 로직
def check_and_summarize(input_text, model_pipeline, max_length) :
    text_length =  len(input_text)
    text_start_pointer = 0
    text_end_pointer = 0
    return_text = []
    while True :
        if max_length < text_length - text_start_pointer: 
            pass
        else :
            return_text.append(model_pipeline.summarizer(input_text[text_start_pointer:]))
            return return_text


        
    
@app.post("/summarize/text")
async def summarize_text(text: TextItem):
    after_preproces = textProcessing(text.text)
    textmodel = summarize_model.summarizer(after_preproces, min_length=32, max_length=len(after_preproces) / 2)
    return {'message': textmodel}


def main():
    pass
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8908  )