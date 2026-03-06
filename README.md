# ai-mmoprg 실행 가이드

이 문서는 **`ai-mmoprg` 저장소를 처음 받았을 때, 어떻게 실행 준비를 하고 어떤 순서로 확인하면 되는지**를 자세히 설명합니다.

> 현재 저장소에는 애플리케이션 소스 코드/실행 스크립트가 아직 포함되어 있지 않습니다. 따라서 이 문서는 **실행 환경 표준화 + 향후 코드 추가 시 바로 사용할 실행 절차** 중심으로 구성되어 있습니다.

---

## 1) 빠른 시작(Quick Start)

아래 명령으로 저장소를 클론하고 진입합니다.

```bash
git clone <YOUR_REPOSITORY_URL>
cd ai-mmoprg
```

현재 기준으로는 실행 가능한 앱이 없으므로, 아래처럼 저장소 상태를 먼저 확인합니다.

```bash
git status
ls -la
```

---

## 2) 권장 개발 환경

실행/개발 환경을 통일하기 위해 다음 도구 설치를 권장합니다.

- **Git**: 버전 관리
- **Docker + Docker Compose**: 환경 재현성 확보(권장)
- **런타임(프로젝트 채택 후 선택)**
  - Node.js 20+ (웹/게임 서버를 JS/TS로 구성할 경우)
  - Python 3.11+ (AI/시뮬레이션 로직을 Python으로 구성할 경우)

### 버전 확인 명령

```bash
git --version
docker --version
docker compose version
node --version      # Node 사용 시
python --version    # Python 사용 시
```

---

## 3) 실행 방식 선택 가이드

프로젝트가 커지면 실행 방식이 2가지로 나뉘는 경우가 많습니다.

### A. 로컬 직접 실행

- 장점: 빠른 반복 개발
- 단점: 팀원별 환경 차이 발생 가능

### B. Docker 실행(권장)

- 장점: 팀 전체 동일 환경
- 단점: 초기 설정 필요

> 팀 프로젝트라면 **Docker 우선**, 개인 실험/프로토타이핑은 **로컬 직접 실행**을 추천합니다.

---

## 4) (권장) 표준 실행 스크립트 규칙

아직 코드가 없기 때문에, 이후 코드 추가 시 아래 규칙을 맞추면 README만 보고 누구나 실행 가능합니다.

### 루트 기준 표준 명령

```bash
# 의존성 설치
make setup

# 개발 서버 실행
make dev

# 테스트 실행
make test

# 린트/포맷 검사
make lint

# 프로덕션 실행
make start
```

`Makefile`을 사용하면 언어나 프레임워크가 달라도 실행 진입점이 통일되어 운영이 쉬워집니다.

---

## 5) 언어별 실행 예시 템플릿

실제 코드가 들어오면 아래 중 해당 스택을 선택해 README를 구체화하세요.

### 5-1) Node.js/TypeScript 예시

```bash
npm install
npm run dev
npm test
npm run build
npm run start
```

권장 스크립트(`package.json`):

- `dev`: 개발 서버
- `test`: 단위 테스트
- `build`: 빌드
- `start`: 배포 실행
- `lint`: 정적 분석

### 5-2) Python 예시

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
pytest
```

권장 파일:

- `requirements.txt` 또는 `pyproject.toml`
- `app/main.py`(진입점)
- `tests/` 디렉터리

---

## 6) 환경 변수(.env) 관리

실행 오류의 대부분은 환경 변수 누락에서 발생합니다.

1. `.env.example` 제공
2. 개발자는 `.env` 복사 후 값 수정
3. 비밀값은 Git 커밋 금지

```bash
cp .env.example .env
```

권장 키 예시:

- `APP_ENV=development`
- `PORT=3000`
- `DATABASE_URL=...`
- `REDIS_URL=...`

---

## 7) Docker 기반 실행 템플릿

`docker-compose.yml`이 준비되면 다음 순서로 실행합니다.

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f
```

종료:

```bash
docker compose down
```

데이터까지 초기화:

```bash
docker compose down -v
```

---

## 8) 실행 확인 체크리스트

코드가 추가된 이후에는 아래를 순서대로 점검하면 대부분의 문제를 빠르게 찾을 수 있습니다.

1. 의존성 설치가 성공했는가?
2. `.env`가 최신 형식인가?
3. 포트 충돌이 없는가?
4. DB/캐시 등 외부 서비스가 켜져 있는가?
5. `test`/`lint`가 통과하는가?

---

## 9) 자주 발생하는 문제(트러블슈팅)

### 포트 충돌

증상: `Address already in use`

해결:
- 다른 프로세스 종료
- `.env` 또는 설정 파일에서 포트 변경

### 환경 변수 누락

증상: 시작 직후 설정 관련 예외

해결:
- `.env.example` 대비 누락 키 확인
- 값 포맷(따옴표, 공백) 재검증

### 컨테이너는 뜨는데 서비스 접속 불가

해결:
- `docker compose ps`에서 포트 매핑 확인
- `docker compose logs -f <service>`로 에러 확인
- 서비스 bind 주소를 `0.0.0.0`으로 설정

---

## 10) 협업을 위한 운영 규칙(권장)

- 새 기능 추가 시 반드시 아래 3종 갱신
  1. 실행 명령(`Makefile`/스크립트)
  2. 환경 변수 예시(`.env.example`)
  3. README 실행 섹션
- PR 템플릿에 실행/검증 결과를 첨부
- "README만 보고 신규 인원이 실행 가능" 상태 유지

---

## 11) 현재 저장소 상태 요약

- 현재는 초기화 상태(`.gitkeep`)이며 실행 대상 프로그램은 아직 없습니다.
- 따라서 본 문서는 **향후 개발을 위한 실행 표준/템플릿 문서**입니다.
- 코드가 추가되면 4~9장을 프로젝트 실제 명령에 맞게 즉시 업데이트하세요.

