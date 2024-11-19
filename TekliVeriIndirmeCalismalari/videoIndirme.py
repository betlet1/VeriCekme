from bs4 import BeautifulSoup
import requests

video = requests.get('http://www.howtowebscrape.com/examples/media/images/BigRabbit.mp4')
with open('BigRabbit.mp4', 'wb') as file:
    for chunk in video.iter_content(chunk_size=1024):
        file.write(chunk)
        
        print(chunk)