import requests
from bs4 import BeautifulSoup

# Spotify sayfasının URL'sini belirt
url = "https://open.spotify.com/playlist/37i9dQZF1E4s5TBYceCHdn"  # İlgili çalma listesinin ID'sini ekle
response = requests.get(url)

# İstek başarılı mı kontrol et
if response.status_code == 200:
    # HTML içeriğini al
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Şarkı başlıklarını bul (HTML yapısına bağlı olarak değişebilir)
    # Örneğin, şarkı başlıkları <h3> etiketinde veya belirli bir class adı ile yer alabilir
    song_titles = soup.find_all('a')  # Uygun sınıf adını değiştir
    
    # Şarkı başlıklarını ekrana yazdır
    for title in song_titles:
        print(title.text)
else:
    print(f"İstek başarısız oldu: {response.status_code}")