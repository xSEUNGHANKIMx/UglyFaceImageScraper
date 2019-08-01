from selenium import webdriver

import urllib.request as urllibreq
import json
import time
import os
import ctypes
import datetime
import requests

# adding path to geckodriver to the OS environment variable
os.environ["PATH"] += os.pathsep + os.getcwd()
DRIVE = u'e:'
# ROOT = DRIVE + os.sep + "Dataset"
ROOT = "/data/sie/data_source/ugly_faces/web_scrap"
DOWNLOAD_LIMIT = 200
TIME_OUT = 15
SCROLL_COUNT = 4


def main():
	if not os.path.exists(ROOT):
		os.makedirs(ROOT)

	total_downloaded_count = 0
	header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'}
	extensions = {"jpg", "jpeg", "png", "gif"}

	f = open('search_keywords.txt')
	line = f.readline()

	while line:
		sub_trying_count = 0
		sub_downloaded_count = 0
		search_keyword = str(line).replace('\r', '').replace('\n', '')
		save_path = ROOT + os.sep + search_keyword.replace(' ', '_')

		if not os.path.exists(save_path):
			os.makedirs(save_path)

		print('Search Text:', search_keyword)
		url = "https://www.google.com/search?q=" + search_keyword.replace(' ', '%20') + "&source=lnms&tbm=isch"

		driver = webdriver.Firefox()
		driver.get(url)
		driver.minimize_window()

		for _ in range(int(SCROLL_COUNT)):
			for __ in range(10):
				# multiple scrolls needed to show all 400 images
				driver.execute_script("window.scrollBy(0, 1000000)")
				time.sleep(0.2)
			# to load next 400 images
			time.sleep(0.5)
			try:
				driver.find_element_by_xpath("//input[@value='Show more results']").click()
			except Exception as e:
				print("Less images found:", e)
				break

		images = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
		print("Total searched images:", len(images))
		for img in images:
			sub_trying_count += 1
			success = False
			image_fullpath = ""
            
			try:
				img_url = json.loads(img.get_attribute('innerHTML'))["ou"]
				img_type = json.loads(img.get_attribute('innerHTML'))["ity"]
				print(img_url)

			except Exception as e:
				pass
				print('    xXx -> Failed: json query failed:', e)
			else:
				try:
					if img_type not in extensions:
						img_type = 'jpg'

					file_name = '_'.join([search_keyword, str(sub_downloaded_count)]) + '.' + img_type
					image_fullpath = os.path.join(save_path, file_name)

					content = requests.get(img_url, timeout=TIME_OUT).content
					if content is not None:
						file = open(image_fullpath, 'wb')
						file.write(content)
						file.close()
				except Exception as e:
					print('    xxxXXXXXxxx(1) -> Failed'.format(img_url), e)
					print("save_path: ", save_path)
					try:
						urllibreq.urlretrieve(img_url, image_fullpath, timeout=TIME_OUT)
					except Exception as e:
						pass
						print('    xxxXXXXXxxx(2) -> Failed'.format(img_url), e)
					else:
						success = True

				else:
					success = True

				finally:
					if os.path.isfile(image_fullpath) and os.path.getsize(image_fullpath) > 0:
						if success:
							print('  oooOOOOOooo-> Success')
							sub_downloaded_count += 1
					else:
						pass
						print('  xxxXXXXXxxx -> Failed: File is Empty!')

			if sub_downloaded_count >= DOWNLOAD_LIMIT:
				break;

		print("Sub. Total Downloaded: ", sub_downloaded_count, "/", sub_trying_count, "\n")
		total_downloaded_count += sub_downloaded_count
		driver.quit()


		line = f.readline()

	f.close()
	print("\nFinish Downloading! Total Downloaded: ", total_downloaded_count)

if __name__ == "__main__":
	main()
