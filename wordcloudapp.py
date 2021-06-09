import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re
from konlpy.tag import Okt
from collections import Counter
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from wordcloud import WordCloud
import stylecloud
import re
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtGui
from PyQt5 import uic

form_class = uic.loadUiType("wordcloudapp.ui")[0]

class wordcloudApp(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.cats = {'속보': '001', '정치': '100', '경제': '101', '사회': '102', '생활/문화': '103',
                '세계': '104', 'IT/과학': '105', '연예 속보': '106', '스포츠 속보': '107',
                '오피니언': '110'}

        self.fill_cat_comboBox()
        self.fill_ymd_comboBox()
        self.fill_wc_shape_comboBox()
        self.btn_start.clicked.connect(self.web_scraping)

    def fill_wc_shape_comboBox(self):
        self.wc_shape.addItem('디자인을 선택하세요')
        icons = self.get_wordcloud_shape()
        for icon in icons:
            self.wc_shape.addItem(str(icon))

    def get_wordcloud_shape(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")

        wd = webdriver.Chrome('/home/ai106/PycharmProjects/pythonProject/NLP/chromedriver', options=options)

        url = "https://www.joydeepdeb.com/misc/font-awesome-5.html"

        wd.get(url)

        html = wd.page_source
        soup_ = BeautifulSoup(html, 'html.parser')
        icons_soup = soup_.find_all('i')

        icons = []
        for icon in icons_soup:
            icons.append(icon.attrs['class'])
        icons = icons[24:]
        icons = icons[:100]
        icons = [icon[1] + ' ' + icon[2] for icon in icons]
        return icons

    def fill_cat_comboBox(self):
        for cat in self.cats.keys():
            self.category.addItem(str(cat))

    def fill_ymd_comboBox(self):
        self.s_year.addItem('시작연도')
        self.e_year.addItem('종료연도')
        self.s_month.addItem('시작달')
        self.e_month.addItem('종료달')
        self.s_date.addItem('시작일')
        self.e_date.addItem('종료일')

        for year in range(1990, 2022):
            self.s_year.addItem(str(year))
            self.e_year.addItem(str(year))
        for month in range(1, 13):
            self.s_month.addItem(str(month))
            self.e_month.addItem(str(month))
        for date in range(1, 32):
            self.s_date.addItem(str(date))
            self.e_date.addItem(str(date))

    def get_date_range(self):
        try:
            s_year = self.s_year.currentText()
            s_month = self.s_month.currentText()
            s_date = self.s_date.currentText()
            e_year = self.e_year.currentText()
            e_month = self.e_month.currentText()
            e_date = self.e_date.currentText()
            start = str(s_year) + str(s_month).zfill(2) + str(s_date).zfill(2)
            end = str(e_year) + str(e_month).zfill(2) + str(e_date).zfill(2)
            dates_ = set(range(int(start), int(end)+1))
            dates = []
            for date in dates_:
                if int(str(date)[4:6]) < 13:
                    if int(str(date)[6:]) < 32:
                        dates.append(str(date))
            return dates
        except:
            print('날짜지정오류')

    def web_scraping(self):
        self.dates = self.get_date_range()
        self.cat = self.cats[str(self.category.currentText())]
        self.wc_icon = str(self.wc_shape.currentText())

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        # # 혹은 options.add_argument("--disable-gpu")
        wd = webdriver.Chrome('/home/ai106/PycharmProjects/pythonProject/NLP/chromedriver', options=options)

        pages = list(range(1, 101))

        titles_str = ''
        for date in self.dates:
            print('날짜 : ', date)
            for page in pages:
                print('기사 페이지 :', page)
                naver_url = "https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1={}&date={}&page={}".format(self.cat,
                                                                                                                   date,
                                                                                                                   str(page))

                wd.get(naver_url)
                time.sleep(0.1)
                cur_url = wd.current_url

                if cur_url != naver_url:
                    continue
                else:
                    html = wd.page_source
                    soup_nv = BeautifulSoup(html, 'html.parser')
                    articles = soup_nv.find_all('a', class_='nclicks(fls.list)')
                    for title_area in articles:
                        title = title_area.get_text()
                        titles_str += title
        titles_str = re.sub('\[\w+\]', '', str(titles_str))
        titles_str = re.sub(r'[^\w]', ' ', str(titles_str))
        print('스크래핑한 기사제목들 : \n', titles_str)

        with open("{}_titles_str.txt".format(str(self.cat)), "w") as f:
            f.write(titles_str)

        self.create_wc()

    def create_wc(self):
        stylecloud.gen_stylecloud(file_path="{}_titles_str.txt".format(str(self.cat)),
                                  icon_name=self.wc_icon,
                                  size=1028,
                                  palette="colorbrewer.diverging.Spectral_11",
                                  background_color='black',
                                  font_path="usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
                                  gradient="horizontal",
                                  output_name="{}_naver_wordcloud.png".format(self.cat))

        pixmap = QPixmap('{}_naver_wordcloud.png'.format(self.cat))
        self.label_wc.setPixmap(pixmap)
        self.label_wc.setContentsMargins(10, 10, 10, 10)
        self.label_wc.setScaledContents(True)

    def initUI(self):
        self.setWindowTitle('네이버검색어_워드클라우드')
        # self.resize(1000, 850)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = wordcloudApp()
    form.show()
    sys.exit(app.exec_())




