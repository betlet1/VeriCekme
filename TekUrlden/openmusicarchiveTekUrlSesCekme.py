import requests
from bs4 import BeautifulSoup
import os

# URL: dosyalarin nereden okunacagi
base_url = "https://www.openmusicarchive.org/browse_tag.php?tag=Diamond%20Disc"

# MP3 Dosyalar nerede kaydedilecek
download_dir = "./librivox_mp3s"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# HTML-Iceriginin okunmasi
response = requests.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')

# .mp3 ile biten tüm linklerin contentten okunmasi
mp3_links = soup.find_all('a', href=True)
mp3_links = [link['href'] for link in mp3_links if link['href'].endswith('.mp3')]

# 5000 dosyayi sinirlayalim
max_files = 5000
download_count = 0

# MP3-Dosyalarinin download edilmesi
for mp3_link in mp3_links:
    if download_count >= max_files:
        break  # 5000 dosya indirilmis ise cik

    # Absolute URL olustur
    if not mp3_link.startswith('http'):
        mp3_link = "https://www.openmusicarchive.org/" + mp3_link

    # Dosya ac
    file_name = os.path.join(download_dir, mp3_link.split('/')[-1])

    # MP3-Dosyasi indir ve kaydet
    print(f"Download: {mp3_link}")
    try:
        mp3_response = requests.get(mp3_link)
        with open(file_name, 'wb') as f:
            f.write(mp3_response.content)
        download_count += 1
        print(f"Dosya kaydedildi: {file_name}")
    except Exception as e:
        print(f"dosya indirmede problem yasandi {mp3_link}: {e}")

print("Download islemi bitti!")
