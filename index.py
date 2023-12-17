from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

BASE_URL = "https://everia.club/category/gravure/page/{}"

def get_page_content(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        with requests.Session() as session:
            response = session.get(url, headers=headers)
            response.raise_for_status()  # 检查是否有错误的响应码
            return response.text
    except requests.RequestException as e:
        print(f"Error during request: {e}")
        return None

def parse_page(html_content):
    if html_content is None:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    data = []

    entries = soup.find_all('div', class_='blog-entry-inner')
    for entry in entries:
        thumbnail = entry.find('img', class_='attachment-large')
        link = entry.find('a', class_='thumbnail-link')['href']
        title_element = entry.find('h2', class_='blog-entry-title')

        # 在找不到标题元素时，跳过当前循环
        if title_element is None:
            continue

        title = title_element.text.strip()

        entry_data = {
            'thumbnail': thumbnail['src'] if thumbnail else None,
            'link': link,
            'title': title
        }
        data.append(entry_data)

    return data

def get_images(detail_url):
    html_content = get_page_content(detail_url)
    if html_content is None:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    images = []

    # 提取图片数据
    image_elements = soup.find_all('figure', class_='wp-block-image')
    for image_element in image_elements:
        image_src = image_element.find('img')['src']
        images.append(image_src)

    return images

def process_page(page_number):
    url = BASE_URL.format(page_number)
    html_content = get_page_content(url)
    parsed_data = parse_page(html_content)

    return parsed_data
  
# 页面数据    
@app.route('/api/page/<int:page_number>', methods=['GET'])
def get_page_data(page_number):
    page_data = process_page(page_number)
    return jsonify(page_data)

# 详情页数据
@app.route('/api/detail/<path:detail_url>', methods=['GET'])
def get_images_data(detail_url):
    images_data = get_images(detail_url)
    return jsonify(images_data)

if __name__ == '__main__':
    app.run(debug=True)    
