import http.client
from PIL import Image
from io import BytesIO
import requests

conn = http.client.HTTPSConnection("hapi-books.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "567a545e60msh8fecd6a13c95adbp106bacjsn41754a801cde",
    'x-rapidapi-host': "hapi-books.p.rapidapi.com"
}

conn.request("GET", "/search/moby+dick", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
data = data.decode("utf-8")

# URL da imagem
image_url = data[1]["cover"]

# Fazendo o download da imagem
response = requests.get(image_url)
if response.status_code == 200:
    # Abrindo a imagem com Pillow
    img = Image.open(BytesIO(response.content))
    
    # Exibindo a imagem
    img.show()
else:
    print("Falha ao baixar a imagem.")