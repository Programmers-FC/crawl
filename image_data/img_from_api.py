from PIL import Image
from io import BytesIO

for player_id in list:
    urlString = f"https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{player_id}.png"
    response = requests.get(urlString)
    image = Image.open(BytesIO(response.content))
    image.save(f"C:\\Users\\user\\Downloads\\{player_id}.png")# 사진 개당 평균 크기는 25.9KB #경로 지정 필수

