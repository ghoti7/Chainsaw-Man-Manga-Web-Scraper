import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

BASE_URL = 'https://chainsawmann.com'
BASE_CHAPTER_URL = 'https://chainsawmann.com/manga/chainsaw-man-chapter-'


def craft_chapter(chapter_url, download_images):
	chapter_number = chapter_url.strip('/').split('-')[-1]
	html_head = f'''<!DOCTYPE html>
	<html lang="en">
	  <head>
	    <meta charset="UTF-8">
	    <meta name="viewport" content="width=device-width, initial-scale=1.0">
	    <meta http-equiv="X-UA-Compatible" content="ie=edge">
	    <link rel="stylesheet" href="{os.path.join('..', '..', 'style.css')}">
	    <title>Chapter {chapter_number}</title>
	  </head>
	  <body>
	  	<h1>Chapter {chapter_number}</h1>
	'''

	html_body = ''

	try:
		response = requests.get(chapter_url)
		if response.status_code != 200:
			return 1
	except:
		return 1

	soup = BeautifulSoup(response.text, 'html.parser')
	pics_container = soup.find('div', class_=['post-body', 'entry-content'])


	image_links = []
	for a in pics_container.find_all('a'):
		url = a['href']
		image_links.append(url)


	html_body += '<div id="manga-viewer">'

	save_dir = os.path.join('Chapters', 'Chapter ' + chapter_number)
	if not os.path.exists(save_dir):
		os.mkdir(save_dir)


	if download_images == 'y':
		counter = 1
		for image_link in image_links:
			try:
				image = requests.get(image_link).content
				image_path = os.path.join(save_dir, f'page {counter}.jpg')
				#image.raise_for_status()
				with open(image_path, 'wb') as file:
					file.write(image)
			except:
				print(len(image_link))
				print(f'[-] An error occured. Failed to download page {counter} from chapter {chapter_number}')

			width_class = ''
			if Image.open(BytesIO(image)).size[0] == 2133:
				width_class = 'wide'
			 
			html_body += f'<img src="page {counter}.jpg" class="{width_class}">'
			counter += 1
	else:
		for image_link in image_links:
			image = requests.get(image_link).content
			width_class = ''

			if Image.open(BytesIO(image)).size[0] == 2133:
				width_class = 'wide'

			html_body += f'<img src={image_link} class="{width_class}">'


	html_body += '</div>'
	html_footer = '</body>\n</html>'

	full_html = html_head + html_body + html_footer


	with open(os.path.join(save_dir, 'index.html'), 'w', encoding='utf-8') as file:
		file.write(full_html)

	return 0


def validate_int(numbers):
	for number in numbers:
		try:
			if not (1 <= int(number) <= 2133):
				print("[-] Numbers must be between 1 and 213 inclusively")
				return 1
		except:
			print('[-] Numbers must be valid integers')
			return 2

	return 0


def check_and_load(numbers, download_images):
	for number in numbers:
		file_path = os.path.join('Chapters', 'Chapter ' + str(number), 'index.html')
		if not os.path.exists(file_path):
			code = craft_chapter(BASE_CHAPTER_URL + str(number), download_images)
			if code != 0:
				print(f'[-] An error ocurred. The chapter {number} was not loaded')


def show_info():
	print('a) - load specific chapters')
	print('b) - load a range of chapters')
	print('c) - list my chapters')
	print('d) - show this info again')
	print('q) - quit')

show_info()


while True:
	cmd = input('\n> What do you want to do?: ').strip(' ')

	if cmd == 'a':
		numbers = input('\n> Chapter number(s): ').strip(' ').split(' ')

		if validate_int(numbers) != 0:
			continue

		download_images = input('Do you want to download the images (y/n)?: ')
		check_and_load(numbers, download_images)


	elif cmd == 'b':
		first, second = input('From chapter: ').strip(' '), input('To chapter: ').strip(' ')

		if validate_int([first, second]) != 0:
			continue

		download_images = input('Do you want to download the images (y/n)?: ')
		check_and_load(range(int(first), int(second) + 1), download_images)


	elif cmd == 'd':
		show_info()


	elif cmd == 'q':
		print('\nSee you next time!\n')
		exit()
