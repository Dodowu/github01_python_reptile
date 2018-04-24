from lxml import etree
from fontTools.ttLib import TTFont
from io import BytesIO
import requests
import csv
import re

headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
}

url = 'https://www.qidian.com/all?page=1'
def get_font(url):
	
	res = requests.get(url, headers=headers)
	html = etree.HTML(res.text)
	word_link = re.compile(r">(.*?);<")
	ele_word = html.xpath('/html/body/div[2]/div[5]/div[2]/div[2]/div/ul/li[1]/div[2]/p[3]/span/span')[0]
	# print(ele_word)
		# ele_word = each.find('div/p[@class="update"]/span/span')
	encry_text = etree.tostring(ele_word).decode()
	# print(encry_text)
	groups = word_link.search(encry_text)
	# print(groups)
	encry_text = groups.group(1)
	return encry_text
	

def get_url(url):
	res = requests.get(url, headers=headers)
	html = etree.HTML(res.text)
	# word_link = re.compile(r">(.*?);<")
	ele_word = html.xpath('/html/body/div[2]/div[5]/div[2]/div[2]/div/ul/li[1]/div[2]/p[3]/span/style/text()')[0].encode('utf-8')

	return ele_word
	

def get_font_code(ele_word, encry_text):
	WORS_MAP = {'period':'.', 'zero':'0', 'one':'1', 'two':'2', 'three':'3', 'four':'4', 'five':'5', 'six':'6', 'seven':'7', 'eight':'8', 'nine':'9' }
	url = str(ele_word,encoding='utf-8').split("'")[5]
	res = requests.get(url,headers=headers)
	font = TTFont(BytesIO(res.content))
	cmap = font.getBestCmap()
	font.close()

	word_count= ''
	for flag in encry_text.split(";"):
		ch = cmap.get(int(flag[2:]))
		word_count += WORS_MAP.get(ch, '')
	return word_count

if __name__ == '__main__':
	word_counts = []
	encry_text = get_font(url)
	url = get_url(url)
		
	word_count = get_font_code(url, encry_text)
	print(word_count)
