import io
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# Google Drive API için ayarlar
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'dosyaAdi.json'  # JSON dosyanızın adı
FOLDER_ID = ''  # Yüklemek istediğiniz klasörün ID'si

# Yetkilendirme Bilgilerini Ayarla
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Google Drive Servisini Başlat
service = build('drive', 'v3', credentials=credentials)

# Google Drive'a dosya yükleme fonksiyonu
def upload_file(file_stream, file_name):
    file_metadata = {
        'name': file_name,
        'parents': [FOLDER_ID]  # Yüklemek istediğiniz klasörün ID'si
    }

    media = MediaIoBaseUpload(file_stream, mimetype='audio/wav')

    # Dosyayı yükle
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Dosya yüklendi: {file_name} (ID: {file['id']})")

# Çerezler ve başlıklar
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

# İndirme işlemi fonksiyonu
def download_file(url, cookies, headers):
    file_name = url.split("/")[-1]
    try:
        # Dosyayı belleğe indir
        response = requests.get(url, cookies=cookies, headers=headers, stream=True)
        if response.status_code == 200:
            file_stream = io.BytesIO(response.content)
            print(f"Dosya belleğe indirildi: {file_name}")

            # Google Drive'a yükle
            upload_file(file_stream, file_name)
        else:
            print(f"İndirme başarısız oldu: {response.status_code}")
    except Exception as e:
        print(f"İndirme hatası: {e}")


# Tarayıcıyı başlatma
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Freesound giriş sayfasına gitme
driver.get('https://freesound.org/')

# Giriş butonuna tıklayın (Modal açılacak)
login_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//button[@data-toggle="login-modal"]'))
)
login_button.click()

# Modal açılmasını bekleyin (Form elemanlarını içeren modal)
WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "loginModal"))
)

# Kullanıcı adı ve şifre alanlarını bulun
username_field = driver.find_element(By.ID, 'id_username')
password_field = driver.find_element(By.ID, 'id_password')

# Giriş için kullanıcı adı ve şifre
username = 'Kullanıcı adı'  # Kendi kullanıcı adınızı buraya yazın
password = 'Şifre'  # Kendi şifrenizi buraya yazın
username_field.send_keys(username)  # Kullanıcı adını girme
password_field.send_keys(password)  # Şifreyi girme
# Giriş formunu gönderin
password_field.send_keys(Keys.RETURN)

# Giriş işlemini tamamlamayı bekleme ve mesaj yazdırma
try:
    WebDriverWait(driver, 10).until(
        EC.url_changes('https://freesound.org/')
    )
    print("Giriş başarıyla tamamlandı!")
except Exception as e:
    print(f"Giriş işlemi başarısız: {e}")

# Sayfalar arasında gezinme ve şarkı linklerini indirme
def scrape_sounds():
    for page in range(1, 351):  # 350 sayfa gezilecek
        print(f"Sayfa {page} yükleniyor...")
        driver.get(f'https://freesound.org/search/?q=music&f=type%3A%22wav%22&page={page}#sound')
        time.sleep(2)

        # Sayfada ses linklerini bulma ve URL'leri listeye ekleme
        sound_links = driver.find_elements(By.XPATH, '//a[contains(@class, "bw-link--black") and starts-with(@href, "/people/")]')
        sound_urls = [link.get_attribute("href") for link in sound_links if link.get_attribute("href")]
        print(f"{len(sound_urls)} adet ses linki bulundu.")

        if len(sound_urls) <= 1:
            print("Yeterli ses linki yok. Devam ediliyor...")
            continue

        for index, sound_page_url in enumerate(sound_urls[1:], start=2):  # İlk linki atlamak için [1:] kullanıldı
            try:
                print(f"{index}. linke gidiliyor: {sound_page_url}")
                driver.get(sound_page_url)
                time.sleep(2)

                # İndirme butonunu bekleyin
                download_button = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//a[contains(@class, "sound-download-button") and @href]')
                    )
                )
                print("İndirme butonu bulundu.")

                # İndirme URL'sini al
                download_url = download_button.get_attribute("href")
                if not download_url or not download_url.endswith(".wav"):
                    print(f"Geçersiz indirme linki: {download_url}")
                    continue

                # Dosyayı indirin
                download_file(download_url, cookies, headers)
            except Exception as e:
                print(f"Hata oluştu: {e}. İşleme devam ediliyor...")

        print(f"Sayfa {page} işlem tamamlandı.")


# İndirme işlemini başlat
scrape_sounds()

# Tarayıcıyı kapatma
driver.quit()
