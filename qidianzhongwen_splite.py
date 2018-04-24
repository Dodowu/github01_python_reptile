'''起点中文网的小说字数使用了反爬字体，对于此请参照 https://www.cnblogs.com/small-bud/p/8783564.html 学习'''
import xlwt
import requests
from lxml import etree
from fontTools.ttLib import TTFont
from io import BytesIO
import time
import re

#请求头
headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
}

#存储爬出来的数据
all_info_list = []
#反爬字典
WORS_MAP = {'period':'.', 'zero':'0', 'one':'1', 'two':'2', 'three':'3', 'four':'4', 'five':'5', 'six':'6', 'seven':'7', 'eight':'8', 'nine':'9' }

#获得小说字数
def get_word(cmap, encry_text):

	word_count= ''
	for flag in encry_text.split(";"):
		ch = cmap.get(int(flag[2:]))
		word_count += WORS_MAP.get(ch, '')
	return word_count

#获得字数的字体文件
def get_cmap(url):
	res = requests.get(url, headers=headers)
	html = etree.HTML(res.text)
	# word_link = re.compile(r">(.*?);<")
	ele_word = html.xpath('/html/body/div[2]/div[5]/div[2]/div[2]/div/ul/li[1]/div[2]/p[3]/span/style/text()')[0].encode('utf-8')
	
	url = str(ele_word,encoding='utf-8').split("'")[5]
	res = requests.get(url,headers=headers)
	font = TTFont(BytesIO(res.content))
	cmap = font.getBestCmap()
	font.close()

	return cmap

def get_info(url):

	cmap = get_cmap(url)
	html = requests.get(url, headers=headers)
	selector = etree.HTML(html.text)
	word_link = re.compile(r">(.*?);<")
	infos = selector.xpath('//ul[@class="all-img-list cf"]/li')

	for info in infos:
		title = info.xpath('div[2]/h4/a/text()')[0]
		author = info.xpath('div[2]/p[1]/a[1]/text()')[0]
		style_1 = info.xpath('div[2]/p[1]/a[2]/text()')[0]
		style_2 = info.xpath('div[2]/p[1]/a[3]/text()')[0]
		style = style_1 + '.' + style_2
		complete = info.xpath('div[2]/p[1]/span/text()')[0]
		introduce = info.xpath('div[2]/p[2]/text()')[0].strip()

		#获得字体的html源码，再根据字体文件和字典解密
		ele_word = info.xpath('div[2]/p[3]/span/span')[0]
		encry_text = etree.tostring(ele_word).decode()
		groups = word_link.search(encry_text)
		encry_text = groups.group(1)
		word = get_word(cmap, encry_text) + '万字'

		info_list = [title, author, style, complete, introduce, word]
		all_info_list.append(info_list)
	time.sleep(1)

if __name__ == '__main__':
	urls = ['https://www.qidian.com/all?page={}'.format(str(i)) 
			for i in range(1,3)]
	for url in urls:
		get_info(url)

	header = ['title', 'author', 'style', 'complete', 'introduce', 'word']
	book = xlwt.Workbook(encoding='utf-8')
	sheet = book.add_sheet('sheet1')
	for h in range(len(header)):
		sheet.write(0,h,header[h])
	i = 1
	for list in all_info_list:
		j = 0
		for data in list:
			sheet.write(i,j,data)
			j += 1
		i += 1

	book.save('xiaoshuo.xls')
