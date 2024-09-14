import os
import requests
import zipfile
import sys

def get_latest_chrome_driver_version():
    response = requests.get('https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE')
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise Exception('Failed to fetch the latest ChromeDriver version.')

def download_chrome_driver(version, download_path):
    url = f'https://storage.googleapis.com/chrome-for-testing-public/{version}/win64/chromedriver-win64.zip'
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(download_path, 'wb') as f:
            f.write(response.content)
    else:
        raise Exception('Failed to download ChromeDriver.')

def extract_zip(file_path, extract_to):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def setup_chrome_driver():
    try:
        version = get_latest_chrome_driver_version()
        download_path = os.path.join(os.getcwd(), 'chromedriver.zip')
        extract_to = os.getcwd()
        download_chrome_driver(version, download_path)
        extract_zip(download_path, extract_to)
        os.remove(download_path)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
