import os
import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# Google Drive API için ayarlar
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = 'dosyaAdi.json'  # JSON dosyanızın adı
FOLDER_ID = ''  # Yüklemek istediğiniz klasörün ID'sini buraya ekleyin

# Yetkilendirme Bilgilerini Ayarla
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Google Drive Servisini Başlat
service = build('drive', 'v3', credentials=credentials)

BASE_URL = "https://freemusicarchive.org/music/charts/this-week?sort=listens&pageSize=20&page="
MAX_SONGS = 5200  # 52 sayfa x 100 şarkı = 5200 şarkı
SONGS_PER_PAGE = 20  # Sayfa başına şarkı sayısı

download_count = 0

# Chrome WebDriver başlatma
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Sayfa kaydırma fonksiyonu
def scroll_page():
    """Sayfayı kaydırarak yeni içeriklerin yüklenmesini sağlar."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Yeni içeriklerin yüklenmesi için bekle

# Şarkı bilgilerini almak için bu fonksiyonu kullanacağız
def fetch_songs_from_page(page_url):
    """Verilen sayfadaki şarkı bağlantılarını alır."""
    global download_count

    driver.get(page_url)
    time.sleep(2)  # Sayfa yüklenmesi için bekle

    # Sayfadaki her şarkıyı bul
    song_links = []
    song_divs = driver.find_elements(By.CLASS_NAME, "play-item")
    for song_div in song_divs:
        try:
            track_info = song_div.get_attribute("data-track-info")
            if track_info:
                song_info = json.loads(track_info)  # Güvenli olmayan eval(), alternatif çözüm
                song_title = song_info.get("title")
                artist_name = song_info.get("artistName")
                download_url = song_info.get("downloadUrl")
                genre = song_info.get("genre", "Unknown")

                # URL'yi düzelt
                if download_url:
                    download_url = download_url.replace("\\/", "/").replace("\\", "")

                song_links.append({
                    "title": song_title,
                    "artist": artist_name,
                    "download_url": download_url,
                    "genre": genre
                })
        except Exception as e:
            print(f"Hata: Şarkı bilgileri alınırken bir sorun oluştu - {e}")

    return song_links

# Google Drive'a dosya yükleme fonksiyonu
def upload_to_drive(file_content, file_name):
    """Google Drive'a dosya yükler."""
    file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='audio/mp3')
    file = service.files().create(media_body=media, body=file_metadata).execute()
    print(f"Dosya başarıyla Google Drive'a yüklendi: {file['name']}")

def download_and_upload_song(song_info):
    """Verilen şarkıyı indirip, Google Drive'a yükler"""
    global download_count

    try:
        download_link = song_info['download_url']
        song_title = song_info['title']
        artist_name = song_info['artist']

        # Geçerli bir dosya adı oluşturmak için geçerli karakterleri kullan
        song_title = song_title.replace("/", "").replace("\\", "")
        artist_name = artist_name.replace("/", "").replace("\\", "")

        # İstek gönderme
        mp3_response = requests.get(download_link)

        if mp3_response.status_code == 200:  # İçerik tipi kontrolü kaldırıldı
            # Dosyayı Google Drive'a yükle
            upload_to_drive(mp3_response.content, f"{song_title} - {artist_name}.mp3")
            download_count += 1
            print(f"{song_title} indirildi ve Google Drive'a yüklendi. Toplam: {download_count}")
            return True
        else:
            print(f"Hata: {mp3_response.status_code} - Beklenen içerik tipi alınamadı.")
            return False

    except Exception as e:
        print(f"Hata: {song_info['title']} indirilemedi - {e}")
        return False


# Ana süreç
if __name__ == "__main__":
    page_number = 1  # Sayfa numarasına başla
    print("Veriler çekiliyor...")

    while download_count < MAX_SONGS and page_number <= 52:
        current_page_url = BASE_URL + str(page_number)
        print(f"İşleniyor: {current_page_url}")

        # Sayfayı kaydır (İçeriğin yüklenmesi için)
        scroll_page()

        # Sayfadan şarkı linklerini al
        song_links = fetch_songs_from_page(current_page_url)

        if not song_links:
            print(f"Sayfa {page_number} boş veya geçersiz.")
            break

        for song_info in song_links:
            if download_count >= MAX_SONGS:
                print("Toplam indirme sınırına ulaşıldı.")
                break
            download_and_upload_song(song_info)
            time.sleep(2)  # Her şarkı arasında bekleme

        if download_count >= MAX_SONGS:
            print("Toplam indirme sınırına ulaşıldı.")
            break

        page_number += 1  # Sonraki sayfaya geç
        time.sleep(5)  # Sayfalar arasında bekleme

    # Tarayıcıyı kapat
    driver.quit()

    print("İşlem tamamlandı. Toplam indirilen ve Google Drive'a yüklenen şarkı sayısı:", download_count)
