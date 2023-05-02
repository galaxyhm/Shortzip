import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup


class NewsCrawler:
    # naver_crawling_regex = r'(?P<header><br\/>)(?P<value>[ㄱ-ㅎ가-힣a-zA-Z0-9\s.,%\'\"()·“”]+)(?P<tail><br\/>)'
    # naver_crawling_pattern = re.compile(naver_crawling_regex)
    naver_image_caption_regex = r'<em[ㄱ-ㅎ가-힣a-zA-Z0-9\s.,%\'\"()·“‘’”=_>/]+</em>'
    naver_image_caption = re.compile(naver_image_caption_regex)
    naver_news_press_regex = r'alt=\"(?P<extract>[ㄱ-ㅎ가-힣a-zA-Z0-9]+)\"'
    naver_news_press = re.compile(naver_news_press_regex)

    @classmethod
    def navercrawl(cls, url: str) -> dict:
        '''
        url검사 x 
        naver 뉴스일때 크롤링 하는 함수
        '''
        # 이거 안붙이면 nave가 봇으로 인식
        headers = {'User-Agent': 'Mozilla/5.0'}
        web_page = requests.get(url, headers=headers)
        if web_page.status_code != 200:
            return 'error : can\'t get html'
        soup = BeautifulSoup(web_page.content, 'html.parser')
        html = str(soup.select('#dic_area'))
        title = str(soup.select('#title_area > span'))

        article_date = str(soup.select('.media_end_head_info_datestamp'))
        article_date = article_date.replace(u'[\n\n입력', u'')
        article_date = article_date.replace(u'\n\n기사원문\n]', u'')
        article_date = BeautifulSoup(article_date, "lxml").text

        press = str(soup.select('img.media_end_head_top_logo_img:nth-child(1)'))

        press = cls.naver_news_press.search(press)

        press = press.group(1)

        reporter = str(soup.select(
            '#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_journalist > a > em'))
        reporter = BeautifulSoup(reporter, "lxml").text
        reporter = cls.textProcessing(reporter)

        section = str(soup.select('#contents > div.media_end_categorize > a > em'))
        section = BeautifulSoup(section, "lxml").text
        section = section.replace('[', '')
        section = section.replace(']', '')

        # 구처리 

        # news_data = cls.naver_crawling_pattern.findall(html)
        # news_string =''
        # for data in news_data:
        # news_string += data[1]
        # news_string = news_string.replace(u'\xa0', u' ')
        # return news_string
        # print(url)
        html = cls.naver_image_caption.sub('', str(html))
        cleantext = BeautifulSoup(html, "lxml").text
        title = BeautifulSoup(title, "lxml").text
        title = cls.textProcessing(title)
        cleantext = cls.textProcessing(cleantext)
        article_date_list = cls.transform_datetimestring(article_date)
        return_dict = {
            'title' : title,
            'text' : cleantext,
            'press' : press,
            'reporter' : reporter,
            'section' : section,
            'write_date' : '',
            'modify_date' : -1,
        }
        if len(article_date_list) >1 :
            write_date, modify_date = article_date_list
            return_dict['write_date'] = write_date
            return_dict['modify_date'] = modify_date
        else:
            write_date = article_date_list.pop()
            return_dict['write_date'] = write_date
        return return_dict



        # return title, press, reporter, cleantext, section, article_date,

    @classmethod
    def textProcessing(cls, text: str) -> str:
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

    @classmethod
    def transform_datetimestring(cls, string: str) -> list:
        """
        :param string:
        :return: datetime_string tuple
        """

        article_date_regex = r'입력(?P<in>[0-9]+\.[0-9]+\.[0-9]+\.\s[오전|오후]+\s[0-9]+:[0-9]+)\n+수정(?P<modify>[0-9]+\.[0-9]+\.[0-9]+\.\s[오전|오후]+\s[0-9]+:[0-9]+)'
        only_article_date_regex = r'입력(?P<in>[0-9]+\.[0-9]+\.[0-9]+\.\s[오전|오후]+\s[0-9]+:[0-9]+)'
        # print(str)
        if string.find('수정') != -1:
            regex = re.compile(article_date_regex)
        else:
            regex = re.compile(only_article_date_regex)
        temp_tuple = regex.search(string).groups()
        result_list = []
        for date_str in temp_tuple:

            if date_str.find('오후') == -1:
                date_str = date_str.replace('오전', '')
                date_time_obj = datetime.strptime(date_str, '%Y.%m.%d. %H:%M')
            else:
                date_str = date_str.replace('오후', '')
                date_time_obj = datetime.strptime(date_str, '%Y.%m.%d. %H:%M')
                date_time_obj = date_time_obj + timedelta(hours=12)

            result_list.append(date_time_obj.strftime('%Y-%m-%d %H:%M:%S'))
        return result_list


def main():
    url = 'https://n.news.naver.com/article/007/0000007356'
    k = NewsCrawler.navercrawl(url)
    print(k)


if __name__ == '__main__':
    main()
