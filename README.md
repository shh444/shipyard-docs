# 용접 시스템 통신 프로토콜 웹 매뉴얼 (Sphinx)

이 저장소는 **Sphinx + MyST(Markdown)** 기반으로 구성된 웹 문서입니다.

문서 페이지 구성(총 5페이지):
1. 개요 (index)
2. Modbus 신호 일람
3. 비트필드 / 열거형
4. 에러 / 알람
5. UR 컨트롤러 부록

추가 리소스:
- 시스템/프로그램/하드웨어 다이어그램 PNG는 `docs/_static/images/`에 포함되어 있습니다.
  - 개요: `system_architecture.png`, `hardware_overview.png`
  - Modbus 신호 일람: `modbus_signals_flow.png`
  - UR 부록: `program_structure_detail.png`
- UR 컨트롤러 부록(5장)은 **ModBus Server Data** 표를 기준으로 주소를 정리했습니다.


---

## 1) 로컬에서 venv로 실행/빌드

### 1.1 프로젝트 폴더로 이동

```bash
cd shipyard-docs
```

### 1.2 가상환경(venv) 생성

- Windows

```bash
python -m venv .venv
```

- macOS / Linux

```bash
python3 -m venv .venv
```

### 1.3 가상환경 활성화

- Windows (PowerShell)

```powershell
.venv\Scripts\Activate
```

- macOS / Linux

```bash
source .venv/bin/activate
```

### 1.4 의존성 설치

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 1.5 HTML 빌드

```bash
sphinx-build -b html docs docs/_build/html
```

빌드 결과:
- `docs/_build/html/index.html`

### 1.6 로컬 미리보기(간단)

```bash
python -m http.server 8000 --directory docs/_build/html
```

브라우저 접속:
- http://127.0.0.1:8000

### 1.7 수정 자동 반영(라이브 리로드, 권장)

```bash
sphinx-autobuild docs docs/_build/html --port 8000
```

---

## 2) GitHub Pages 자동 배포 (Actions)

### 2.1 GitHub Pages 설정

GitHub 저장소에서:
- **Settings → Pages → Source** 를 **GitHub Actions** 로 설정

### 2.2 배포 방식

- `main` 브랜치에 push 되면 GitHub Actions가 자동으로 문서를 빌드하고 GitHub Pages로 배포합니다.
- 워크플로 파일: `.github/workflows/pages.yml`

배포 완료 후 주소 예시:
- `https://<username>.github.io/<repo>/`

---

## 3) 문서 수정 위치

- 1장(개요): `docs/index.md`
- 2장(신호 일람): `docs/02_modbus_signals.md`
- 3장(비트필드/열거형): `docs/03_bitfields_enums.md`
- 4장(에러/알람): `docs/04_errors_alarms.md`
- 5장(UR 부록): `docs/05_ur_appendix.md`

---

## 4) (선택) .gitignore 권장

```gitignore
.venv/
__pycache__/
docs/_build/
.DS_Store
Thumbs.db
