import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Chrome başlatma seçenekleri
chrome_options = Options()
chrome_options.add_argument("--headless")  # Headless mod
chrome_options.add_argument("--disable-gpu")  # GPU kullanımını devre dışı bırak

# WebDriver başlatma
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


# İndirilen dosyaların kaydedileceği klasör
download_folder = "sesdosyalari"
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# Çerezler ve başlıklar (tarayıcıdan aldığınız veriler)
cookies = {
    "preferSpectrogram": "",
    "disallowSimultaneousAudioPlayback": "",
    "systemPrefersDarkTheme": "",
    "cookieConsent": "",
    "csrftoken": "",
    "sessionid": ""
}

headers = {
    '     User-Agent, Accept girin     '
}


# Sayfayı gezip, her ses dosyasını indiren fonksiyon
def download_sounds_from_page(page_number):
    base_url = f"https://freesound.org/search/?q=music&page={page_number}#sound"

    # Chrome WebDriver ile sayfayı aç
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(base_url)
    time.sleep(5)  # Sayfa yüklenmesini bekleyin

    # Sayfada bulunan ses dosyalarına ait linkleri alın
    sound_links = driver.find_elements(By.CLASS_NAME, 'bw-link--grey-light')

    for link in sound_links:
        try:
            # Öğeyi görünür hale getirmek için kaydır
            driver.execute_script("arguments[0].scrollIntoView();", link)
            time.sleep(1)  # Kaydırmadan sonra kısa bekleme

            # Linke tıklanabilir hale gelene kadar bekleyin
            driver.execute_script("arguments[0].click();", link)
            time.sleep(2)  # Link tıklandığında sayfa yüklenmesini bekleyin

            # İndirme butonunu bulma ve tıklama
            download_button = driver.find_element(By.CLASS_NAME, 'sound-download-button')
            download_link = download_button.get_attribute('href')

            # Dosyayı indir
            if download_link:
                file_name = download_link.split("/")[-1]
                file_path = os.path.join(download_folder, file_name)
                print(f"Downloading {file_name} to {file_path}")
                response = requests.get(download_link, cookies=cookies, headers=headers, stream=True)

                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Downloaded: {file_name}")
                else:
                    print(f"Failed to download: {download_link}")

        except Exception as e:
            print(f"Error processing sound: {e}")
            continue

    driver.quit()


# Tüm sayfaları dolaşmak için döngü
def download_sounds_from_pages(start_page=1, end_page=5):
    for page_number in range(start_page, end_page + 1):
        print(f"Processing page {page_number}...")
        download_sounds_from_page(page_number)


# Örnek olarak 1-5 sayfa arasında ses dosyalarını indir
download_sounds_from_pages(start_page=1, end_page=5)
