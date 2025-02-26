from PIL import Image
from io import BytesIO

denied_list=[]#이미지 다운로드 못받은 선수 고유 식별자 리스트

for player_id in [img_data_list[i]["id"] for i in range(len(img_data_list))]:
    try:
      
        urlString = f"https://fco.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction/p{player_id}.png"
        
        response = requests.get(urlString)
        
        if response.status_code != 200:
            print(f"❌ {player_id}: HTTP {response.status_code} - 이미지 없음")
            denied_list.append(player_id)
            continue

        
        image = Image.open(BytesIO(response.content))
        
        image.save(f"C:\\Users\\user\\Downloads\\image_data3\\{player_id}.png")#다운로드 받을 로컬 경로
        print(f"✅ {player_id}: 이미지 저장 완료")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ {player_id}: 요청 실패 - {e}")
    except (Image.UnidentifiedImageError, OSError) as e:
        print(f"⚠️ {player_id}: 이미지 열기 실패 - {e}")
