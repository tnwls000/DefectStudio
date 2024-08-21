# S001

### 가상환경 생성

`S001/` 디렉터리로 이동 후 아래 명령어 실행

```bash
# 가상환경 생성
python -m venv venv 

# window 환경에서 venv 켜기
source venv/Scripts/activate

# requirements.txt에 설치된 라이브러리 그대로 다운받기 == build.gradle
# fastapi, uvicorn, redis, redisqueue, celery 설치되어있음
pip install -r requirements.txt

# pip로 install한 라이브러리 requirements.txt에 업데이트
pip freeze > requirements.txt
```

<br>

### run server

```bash
fastapi dev main.py

or

# --reload 옵션주면 코드가 변경될 때마다 서버를 자동으로 재시작
uvicorn main:app --reload
```