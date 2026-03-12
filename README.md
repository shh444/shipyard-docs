# shipyard-docs

용접 시스템 통신 프로토콜 통합 COMM 문서 사이트 초안입니다.

## 포함 내용
- MkDocs Material 기반 문서 사이트 골격
- 로봇 ↔ 팬던트 ↔ 용접기 Modbus TCP 주소 문서화
- 프로젝트 작업 시트 기준 오버라이드 반영
- 비트필드/열거형/시퀀스/에러 코드 정리
- GitHub Pages 배포용 Actions 워크플로
- CSV/JSON 레지스터 카탈로그

## 실행 방법
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

## 빌드
```bash
mkdocs build --strict
```

## 소스 우선순위
1. 프로젝트 작업 시트(업로드된 PNG 기준)
2. `docs/assets/reference/pendant_modbus_tcp_map.pdf`
3. 모순 시 `docs/protocol/source-reconciliation.md`의 최종 판정

## 데이터 파일
- `docs/assets/data/modbus_register_catalog.csv`
- `docs/assets/data/modbus_register_catalog.json`
- `docs/assets/data/source_reconciliation.csv`

## 비고
- 초안 버전: 0.1.0
- 생성일: 2026-03-12
- 일부 레지스터는 현장 검증 전까지 `Reserved/TBD`로 유지했습니다.
