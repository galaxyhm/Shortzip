import re
from datetime import datetime, timedelta
import json
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
    
    @classmethod
    def get_news_comment(cls, url : str) -> list :
        url = url.replace('/mnews','')
        url = url.replace('/newspaper','')
        tot_comment_list = []

        naver_url_regex = r'(http|https)://n.news.naver.com/article/\d+/\d+'
        regex = re.compile(naver_url_regex)
        url = regex.match(url)
        if not url :
            print('error 올바르지 않는 url')
        # return 해서 어떻게 처리하셈 
        url = url[0]
        regex_str =r'https://n.news.naver.com/article/(?P<press>\d+)/(?P<article_id>\d+)'
        regex = re.compile(regex_str)
        press, article_id = regex.findall(url)[0]

        headers = {
        'authority': 'apis.naver.com',
        'accept': '*/*',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        # Requests sorts cookies= alphabetically
        # 'cookie': 'ab.storage.userId.7af503ae-0c84-478f-98b0-ecfff5d67750=%7B%22g%22%3A%22browser-1625985144309-6%22%2C%22c%22%3A1626101500089%2C%22l%22%3A1626101500089%7D; ab.storage.deviceId.7af503ae-0c84-478f-98b0-ecfff5d67750=%7B%22g%22%3A%224cbe130c-6edd-d4aa-a78d-290b003c3592%22%2C%22c%22%3A1626101500094%2C%22l%22%3A1626101500094%7D; ASID=7992e0220000017aaa36664e0000004e; _ga=GA1.2.612969395.1626832328; ab.storage.sessionId.7af503ae-0c84-478f-98b0-ecfff5d67750=%7B%22g%22%3A%2228148006-e01d-7623-b7d1-b4fff0f59b4e%22%2C%22e%22%3A1627919390179%2C%22c%22%3A1627908091281%2C%22l%22%3A1627917590179%7D; MM_NEW=1; NFS=2; NNB=RDIIILNX6JCWE; nx_ssl=2; nid_inf=1665554565; NID_AUT=tP3V5ox533EjyAgkJ1JaqWEnPOhXs2hr3teD39pK972fuXqDWQZXoIOMzICJpa1A; NID_JKL=d393brIzilbjw+7TVvG0OW6Eo22+WIhQAfihItUdgbY=; _naver_usersession_=SPdJTrlTMrn8Udkyn58eo6HL; NID_SES=AAABwJaKJ5FjUAETXL8SAX2HKMUSTt3l8pPu49OSzbGzgKEEMN/ckpP4DbQVHQwTV1hVPWtbpP7Nomg0CbD8TtCpyOYbeq8+OpHb5eWbDsXXCeLHO4epgthLtbQHiBE8spXqEtx/h0D6MzxsIlN4pa8gz51jV+oWzQQNnpQCeaKKLaxcpMfhGXnZv4BK1Rg+TAgUFE9RtExcKjteTL2hB9tKT41C7antdQdhLfVXWUbsJ/q5b62iDZnnZUAANXHnWp/9RI2YyKSn70SVu4Bag+fxA/23OqjCHSbK5RMiNOQKV+Bs7uugaAsMKkH6lGBBIbNDkTXGZ4n1+KbqFwe1kV9oCaPJ+siwXESEqvY0jaLVNAqUATQZjnIMFIYwARw41FTuduxW1IOF7MdP7R3EqOvnqNir2lXW1UfRlHlOtMC4w/tXk8xqJR/HVlZrnltKkMZB5zfyDNvnt02jbOKJcORjmOeVvL+xoCdSXwZclfJzRkC31l43+9jSu4X8RPUfuJILRMHf2e1A0NU7Mwds7h+S//5AD0yUJlPtFFzLvriuD1SMTRXiSwN4pNWBi6UIsPzScRpyLMc8hUE8Bi8jJtGk4e0=; NDARK=N; page_uid=hrKUflprvN8ssNc4Muwssssss3R-382317; BMR=',
        'referer': 'https://n.news.naver.com/article/028/0002595736',
        'sec-ch-ua': '"Whale";v="3", " Not;A Brand";v="99", "Chromium";v="102"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'script',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.108 Whale/3.15.136.18 Safari/537.36',
        }
        params = {
                    'ticket': 'news',
                    'templateId': 'default_society',
                    'pool': 'cbox5',
                    'lang': 'ko',
                    'country': 'KR',
                    'objectId': f'news{press},{article_id}',
                    'pageSize': '100',
                    'indexSize': '10',
                    'page': '1',
                    'currentPage': '0',
                    'moreParam.direction': 'next',
                    'moreParam.prev': '10000o90000op06guicil48ars',
                    'moreParam.next': '1000050000305guog893h1re',
                    'followSize': '100',
                    'includeAllStatus': 'true',
                    'sort' : 'favorite'
                }
        
        response = requests.get('https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json', params=params, headers=headers)
        response.encoding = "UTF-8-sig"
        res = response.text.replace("_callback(","")[:-2]
        temp_comments=json.loads(res)
        # return temp_comments['result']['commentList']
        for comment in temp_comments['result']['commentList']:
            contents =comment['contents']
            contents =contents.replace('\n','')
            sympathyCount = comment['sympathyCount']
            antipathyCount = comment['antipathyCount']
            username = comment['userName']
            temp_dict = {
                'userName' : username,
                'contents' : contents,
                'sympathyCount' : int(sympathyCount),
                'antipathyCount' : int(antipathyCount),

            }
            tot_comment_list.append(temp_dict)

        return tot_comment_list



        



from pprint import pprint

def main():
    url = 'https://n.news.naver.com/article/007/0000007362?ntype=RANKING'
    k = NewsCrawler.get_news_comment(url)
    pprint(k)


if __name__ == '__main__':
    main()

