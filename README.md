# StartOn — 서울 상권 분석 AI 서비스

서울시 상권 데이터를 기반으로 업종 추천, 매출 예측, 지역 비교, 창업 적합도 분석을 제공하는 웹 서비스입니다.

## 기술 스택

- **프론트엔드**: React (Vite)
- **백엔드**: FastAPI
- **DB**: MySQL (AWS RDS)
- **ML**: scikit-learn (RandomForest, ExtraTrees 등)
- **인프라**: Docker / Docker Compose

---

## 1. 사전 준비물

- **Docker Desktop** (필수) — [다운로드](https://www.docker.com/products/docker-desktop/)
  - Windows는 WSL2 + 가상화(Hyper-V)가 켜져 있어야 함. 설치 후 "Engine running"(초록불)이 뜨는지 꼭 확인
- **Git**
- 카카오 개발자 계정 (지도/로그인 기능용, [카카오 개발자센터](https://developers.kakao.com/))

Docker로 실행하면 Python/Node를 로컬에 따로 설치할 필요 없습니다.

---

## 2. 처음 받았을 때 하는 설정 (한 번만)

### 2-1. 저장소 클론

```bash
git clone https://github.com/Allycane/final-project.git
cd final-project
```

### 2-2. 환경변수 파일 만들기

**`front/.env`** (front 폴더 안에 생성, `.env.example` 참고)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_KAKAO_MAP_KEY=발급받은_카카오맵_JavaScript_키
VITE_KAKAO_REST_API_KEY=발급받은_카카오_REST_API_키
VITE_KAKAO_REDIRECT_URI=http://localhost:5173/oauth/kakao/callback
```

**`server/.env`** (server 폴더 안에 생성, `server/.env.example` 참고)

```env
# DB 정보
DB_USER=본인이_준비한_MySQL_계정
DB_PASSWORD=본인이_준비한_MySQL_비밀번호
DB_HOST=본인이_준비한_MySQL_주소
DB_PORT=3306
DB_NAME=fp_db

# JWT 인증 설정
SECRET_KEY=임의의_긴_무작위_문자열
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 카카오 로그인 (서버에서 토큰 검증용)
KAKAO_CLIENT_ID=카카오_개발자센터에서_발급받은_REST_API_키
KAKAO_REDIRECT_URI=http://localhost:5173/oauth/kakao/callback

# --- OpenAI ---
OPENAI_API_KEY=본인_OpenAI_API_키
OPENAI_MODEL=gpt-4o-mini
```

- MySQL은 로컬에 직접 설치하거나, AWS RDS 같은 클라우드 DB 아무거나 사용 가능합니다. `DB_HOST`를 로컬로 쓸 경우 `localhost`로 입력하면 됩니다.
- 테이블 스키마는 서버 실행 시 자동 생성되므로(`Base.metadata.create_all`), DB와 계정만 미리 만들어두면 됩니다.
- `SECRET_KEY`는 로그인 토큰(JWT) 서명에 쓰이는 값으로, 아무 문자열이나 충분히 길고 무작위면 됩니다.
- `KAKAO_CLIENT_ID`는 `front/.env`의 `VITE_KAKAO_REST_API_KEY`와 같은 값을 넣으면 됩니다 (카카오 개발자센터에서 발급받은 REST API 키 하나를 양쪽에 씁니다).
- `OPENAI_MODEL`은 비용/속도에 따라 `gpt-4o-mini`(저렴·빠름) 또는 `gpt-4o`(고품질) 중 선택합니다.

> `.env` 파일은 절대 git에 올리지 마세요 (`.gitignore`에 이미 포함되어 있습니다).

### 2-3. 원본 데이터 파일 준비

`server/data/` 폴더는 용량 문제로 git에 포함되어 있지 않습니다. 아래 2개 CSV 파일을 직접 준비해서 `server/data/` 폴더 안에 넣어야 합니다.
s
| 파일명 | 내용 |
| `location.csv` | 자치구/업종별 위경도 좌표 데이터 (지도 기능용) |
| `seoul_store.csv` | 서울시 상권 분기별 매출/점포수 데이터 (추천·예측 모델용) |

서울시 상권분석 서비스(우리마을가게 상권분석 서비스) 등 서울시 공공데이터를 가공해서 사용한 데이터입니다. 원본 데이터 파일이 없으면 이후 단계(DB 적재, 모델 학습)가 진행되지 않습니다.

### 2-4. DB에 원본 데이터 적재 (최초 1회)

```bash
docker exec -it final_project_api bash
cd scripts
python load_data.py
python seed_categories.py
exit
```

`load_data.py`가 `location.csv`, `seoul_store.csv`를 DB의 `location`, `store` 테이블에 적재합니다. `seed_categories.py`는 업종 대분류/중분류 카테고리를 DB에 채웁니다. 둘 다 여러 번 실행해도 안전합니다 (이미 있는 데이터는 건너뜁니다).

### 2-5. Page 2(매출 예측) 모델 학습 (최초 1회, 선택)

`server/ml/page2/revenue_models.pkl`은 파일 용량이 커서 git에 올라가 있지 않습니다. 매출 예측 기능을 쓰려면 로컬에서 직접 학습시켜야 합니다.

```bash
docker exec -it final_project_api bash
cd scripts/page2
python train_model.py
exit
```

몇 분 정도 걸립니다. (Page 1의 업종 추천 모델은 `server/ml/page1/recommendation_model.pkl`로 이미 git에 포함되어 있어 별도 작업이 필요 없습니다.)

---

## 3. 실행 방법

프로젝트 최상위 폴더(`final-project`)에서:

```bash
docker compose up --build -d
```

- 처음 실행하거나 `requirements.txt`/`package.json`이 바뀌었을 때는 `--build` 꼭 포함
- 이후 코드만 바뀌었을 때는 `--build` 없이 `docker compose up -d`로도 충분

### 접속 주소

| 항목               | 주소                       |
| ------------------ | -------------------------- |
| 프론트엔드         | http://localhost:5173      |
| 백엔드 API         | http://localhost:8000      |
| API 문서 (Swagger) | http://localhost:8000/docs |

### 종료

```bash
docker compose down
```

---

## 4. 잘 안 될 때 확인할 것

**컨테이너 상태 확인**

```bash
docker ps
```

`STATUS`가 `Up`이 아니라 `Restarting`이면 백엔드가 시작하다 에러로 죽고 있는 것입니다.

**에러 로그 확인**

```bash
docker compose logs backend
```

`Traceback`으로 시작하는 부분이 실제 원인입니다. 자주 나오는 원인:

- `ModuleNotFoundError` — 새로 추가된 모듈 파일이 git에 안 올라갔거나, `requirements.txt`에 패키지 추가를 깜빡한 경우
- DB 연결 실패 — `server/.env`의 DB 정보 확인

**Docker Desktop 자체가 안 켜질 때 (Windows)**

- "Virtualization support not detected" 에러가 뜨면, Windows 검색 → "Windows 기능 켜기/끄기" → `Hyper-V`, `Virtual Machine Platform`, `Windows Hypervisor Platform` 전부 체크 후 재부팅
- 안드로이드 에뮬레이터(MuMu, LDPlayer 등)를 같이 쓰는 경우 가상화 방식이 충돌할 수 있음

---

## 5. 프로젝트 구조

```
final-project/
├── front/                      # React 프론트엔드
│   └── src/
│       ├── api/                 # 백엔드 API 호출 함수
│       ├── pages/                # 화면 단위 컴포넌트
│       └── mocks/                # (연동 완료 후 순차적으로 제거 중)
└── server/                      # FastAPI 백엔드
    ├── main.py                   # 앱 진입점, 라우터 등록
    ├── router/                   # API 엔드포인트
    ├── models/                   # SQLAlchemy ORM 모델
    ├── services/                 # 비즈니스 로직 (지도, 랭킹 등)
    ├── database/                  # DB 연결 설정
    ├── scripts/
    │   ├── page1/                 # 업종 추천 모델 학습 스크립트
    │   └── page2/                 # 매출 예측 모델 학습 스크립트
    └── ml/                        # 학습된 모델 파일(.pkl)
        ├── page1/                 # git 포함 (용량 작음)
        └── page2/                 # git 미포함 (직접 학습 필요, 위 2-5 참고)
```

## 6. 주요 기능

- **Page 1 — 업종 추천**: 지역+업종을 선택하면 다음 분기 성장 가능성 기준으로 추천/비추천/참고 업종 제시
- **Page 2 — 매출 예측**: 지역+업종+목표 매출을 입력하면 점포당 평균 매출 추이와 목표 달성 확률 예측
- **지도 분포**: 선택한 지역/업종의 실제 위치를 지도에 표시
- **AI 챗봇**: 상권 관련 질의응답
