import requests
import os

# İndirilen dosyanın URL'si
download_url = "https://freesound.org/people/audiomirage/sounds/767102/download/767102__audiomirage__strange-language.wav"

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

# İndirme işlemi
def download_file(url, cookies, headers, download_folder="sesdosyalari"):
    # Dosya adını URL'den çıkart
    file_name = url.split("/")[-1]

    # Dosya yolu oluştur
    file_path = os.path.join(download_folder, file_name)

    # Çerezlerle birlikte istek gönder
    response = requests.get(url, cookies=cookies, headers=headers, stream=True)

    # İstek başarılıysa, dosyayı kaydet
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Dosya indirildi: {file_path}")
    else:
        print(f"İndirme başarısız oldu: {response.status_code}")

# İndirme fonksiyonunu çağır
download_file(download_url, cookies, headers)
