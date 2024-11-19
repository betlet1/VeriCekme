import requests

# Ses dosyasının URL'si (örnek bir ses dosyası)
url = 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'

# Ses dosyasını indirme
response = requests.get(url)

# Dosya adını belirle
file_name = 'downloaded_audio.mp3'

# İndirilen dosyayı kaydet
with open(file_name, 'wb') as file:
    file.write(response.content)

print(f"{file_name} başarıyla indirildi!")

