from bs4 import BeautifulSoup
import requests
import re
import numpy as np

class NewsCrawler:
    # naver_crawling_regex = r'(?P<header><br\/>)(?P<value>[ㄱ-ㅎ가-힣a-zA-Z0-9\s.,%\'\"()·“”]+)(?P<tail><br\/>)'
    # naver_crawling_pattern = re.compile(naver_crawling_regex)
    naver_image_caption_regex = r'<em[ㄱ-ㅎ가-힣a-zA-Z0-9\s.,%\'\"()·“‘’”=_>/]+</em>'
    naver_image_caption =re.compile(naver_image_caption_regex)
    @classmethod
    def navercrawl(cls, url :str ) -> str:
        '''
        url검사 x 
        naver 뉴스일때 크롤링 하는 함수
        '''
        #이거 안붙이면 nave가 봇으로 인식
        headers = {'User-Agent': 'Mozilla/5.0'}
        web_page=requests.get(url, headers=headers)
        if web_page.status_code != 200 :
            return 'error : can\'t get html'
        soup = BeautifulSoup(web_page.content, 'html.parser')
        html = str(soup.select('#dic_area'))

        # 구처리 

        # news_data = cls.naver_crawling_pattern.findall(html)
        # news_string =''
        # for data in news_data:
            # news_string += data[1]
        # news_string = news_string.replace(u'\xa0', u' ')
        # return news_string
        html = cls.naver_image_caption.sub(str(html))
        cleantext = BeautifulSoup(html, "lxml").text
        return cls.textProcessing(cleantext)


    
    @classmethod
    def textProcessing(cls, text:str) ->str:
        text = text.replace(u'\n', u' ')
        text = text.replace(u'\'', u' ')
        text = text.replace(u'\\\'', u' ')
        text = text.replace(u'[', u'')
        text = text.replace(u']', u'')
        text = text.replace(u'  ', u' ')
        return text.strip()
