
from fastapi import FastAPI
from transformers import pipeline
import uvicorn
from model import UrlItem, TextItem, CommentList
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


binary_model = BinaryTextClassificationModel()
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


# 입력 글자수 체크 밑 로직 미완성
def check_and_summarize(input_text, model_pipeline, max_length):
    text_length = len(input_text)
    text_start_pointer = 0
    text_end_pointer = 0
    return_text = []
    while True:
        if max_length < text_length - text_start_pointer:
            if max_length > text_length - text_end_pointer:
                text_end_pointer = text_length
            else:
                text_end_pointer = text_start_pointer + max_length
            min_text = model_pipeline(input_text[text_start_pointer:text_end_pointer])
            return_text.append(min_text)
            print(min_text)
            # return_text.append(model_pipeline.summarizer(input_text[text_start_pointer:text_start_pointer+1999]))
            text_start_pointer = text_start_pointer+max_length-5
        else:
            # return_text.append(model_pipeline(input_text[text_start_pointer:]))
            min_text = model_pipeline(input_text[text_start_pointer:])
            return_text.append(min_text)
            print(min_text)
            # return_text.append(model_pipeline.summarizer(input_text[text_start_pointer:]))
            return return_text


@app.post("/summarize/text")
async def summarize_text(text: TextItem):
    after_preproces = textProcessing(text.text)
    textmodel = summarize_model.summarizer(after_preproces, min_length=32, max_length=len(after_preproces) / 2)
    return {'message': textmodel}


@app.post('/emotion/text')
async def emotion_text(received_comment: CommentList):
    only_comment_list = []
    received_json = received_comment.dict()
    print(received_json['comments'][1])
    for i in received_json['comments']:
        only_comment_list.append(i['contents'])
    classifier_values = binary_model.classifier(only_comment_list)
    for i in range(len(received_json['comments'])):
        received_json['comments'][i]['emotion'] = classifier_values[i]['label']
        received_json['comments'][i]['emotion_value'] = classifier_values[i]['score']

    return received_json


def main():
    uvicorn.run(app, host='0.0.0.0', port=8908)


if __name__ == '__main__':
    main()