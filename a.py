import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import datetime

def save_image(url, save_dir):
    response = requests.get(url, stream=True, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        file_name = os.path.basename(urlparse(url).path)
        save_path = os.path.join(save_dir, file_name)
        with open(save_path, 'wb') as file:
            file.write(response.content)

def crawl_website(url, save_dir, depth=0, max_depth=3):
    visited_urls = set()
    visited_images = set()

    def recursive_crawl(url, save_dir, depth):
        if url in visited_urls or depth > max_depth:
            return
        visited_urls.add(url)

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        for img_tag in soup.find_all('img'):
            img_url = img_tag.get('src')
            if img_url and img_url not in visited_images:
                visited_images.add(img_url)
                save_image(urljoin(url, img_url), save_dir)

        for link in soup.find_all('a'):
            href = link.get('href')
            if href and (href.startswith('/') or urlparse(href).netloc == urlparse(url).netloc):
                next_url = urljoin(url, href)
                recursive_crawl(next_url, save_dir, depth + 1)

    recursive_crawl(url, save_dir, depth)

# ページのURLを入力
page_url = input("クロールするウェブサイトのURLを入力してください: ")

# 画像を保存するディレクトリ
current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
save_directory = os.path.join('images', current_time)

# 画像保存用のディレクトリが存在しない場合は作成
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# ウェブサイトをクロールして画像を保存
try:
    crawl_website(page_url, save_directory)
    print("画像のクロールが完了しました。保存先ディレクトリ:", save_directory)
except RecursionError:
    print("再帰エラーが発生しました。")
except Exception as e:
    print("エラーが発生しました:", str(e))

