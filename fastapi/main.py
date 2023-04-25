from fastapi import FastAPI
from NewsCrawler import NewsCrawler
from pydantic import BaseModel
import transformers
from transformers import pipeline

app = FastAPI()

class UrlItem(BaseModel):
    url : str


class TextItem(BaseModel):
    text :str


#fast api 시작후 모델 로드및 초기화 (현재 임시로 모델딴거 로드중)
class ModelLoad:
    summarizer = None

    def __init__(self):
        self.summarizer = pipeline("summarization", model="gogamza/kobart-summarization", min_length=32, max_length=1024, tokenizer='gogamza/kobart-summarization')


model = ModelLoad()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# 크롤링후 테스트요약
@app.post("/crawl/naver/")
async def crawl(url : UrlItem):
    a, b = NewsCrawler.navercrawl(url.url)

    text = model.summarizer(b, min_length=32, max_length=len(b)/2)
    print(type(text))
    print(text[0])
    text[0]['summary_text'] = NewsCrawler.textProcessing(text[0]['summary_text'])
    text.append({'text': b})
    return {'message': text}


@app.post("/summarize/text")
async def summarize_text(text : TextItem):
    pass