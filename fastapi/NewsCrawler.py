from bs4 import BeautifulSoup
import requests
import re
import numpy as np

class NewsCrawler:
    # naver_crawling_regex = r'(?P<header><br\/>)(?P<value>[ㄱ-ㅎ가-힣a-zA-Z0-9\s.,%\'\"()·“”]+)(?P<tail><br\/>)'
    # naver_crawling_pattern = re.compile(naver_crawling_regex)
    naver_image_caption_regex = r'<em[ㄱ-ㅎ가-힣a-zA-Z0-9\s.,%\'\"()·“‘’”=_>/]+</em>'
    naver_image_caption =re.compile(naver_image_caption_regex)
    naver_news_press_regex = r'alt=\"(?P<extract>[ㄱ-ㅎ가-힣a-zA-Z0-9]+)\"'
    naver_news_press = re.compile(naver_news_press_regex)
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
        title = str(soup.select('#title_area > span'))
        
        article_date = str(soup.select('.media_end_head_info_datestamp'))
        article_date=article_date.replace(u'[\n\n입력', u'')
        article_date=article_date.replace(u'\n\n기사원문\n]', u'')
        
        press = str(soup.select('img.media_end_head_top_logo_img:nth-child(1)'))
        press = cls.naver_news_press.search(press)
        press = press.group(1)


        repoter = str(soup.select('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_journalist > a > em'))
        repoter = BeautifulSoup(repoter, "lxml").text
        repoter = cls.textProcessing(repoter)


        section = str(soup.select('#contents > div.media_end_categorize > a > em'))
        section = BeautifulSoup(section, "lxml").text
        section = section.replace('[','')
        section = section.replace(']','')

        # 구처리 

        # news_data = cls.naver_crawling_pattern.findall(html)
        # news_string =''
        # for data in news_data:
            # news_string += data[1]
        # news_string = news_string.replace(u'\xa0', u' ')
        # return news_string
        # print(url)
        html = cls.naver_image_caption.sub('',str(html))
        cleantext = BeautifulSoup(html, "lxml").text
        title  = BeautifulSoup(title, "lxml").text
        title = cls.textProcessing(title)
        cleantext = cls.textProcessing(cleantext)
        return title, cleantext


    
    @classmethod
    def textProcessing(cls, text:str) ->str:
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


def main():
    url = 'https://n.news.naver.com/article/022/0003805533'
    k = NewsCrawler.navercrawl(url)
    print(k)

if __name__ == '__main__':
    main()