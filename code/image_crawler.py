from PIL import Image
from io import BytesIO
from tqdm import tqdm
import time
import requests
import os
import json


#json에 있는 데이터 가지고 오기
with open("spid.json",encoding='utf-8') as json_file:
    json_data = json.load(json_file)

#시즌 데이터 제거 후 선수 pid 추출
player_lst = list(set([int(str(i['id'])[3:]) for i in json_data]))

#이미지 저장용 파일
os.makedirs('profile_pic',exist_ok=True)

#프로파일이 없는 선수의 pid 저장
errors = []


for i in tqdm(player_lst):
    src = f"https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/players/p{i}.png"
    time.sleep(0.2)
    try:
        
        response = requests.get(src,headers= {'accept': 'image/png'})
        image = Image.open(BytesIO(response.content))
        image.save(f"./profile_pic/{i}.png")
    except:
        errors.append(i)

#이미지가 없는 pid json으로 저장
with open("no_pic_lst.json", "w") as final:
	json.dump(errors, final)