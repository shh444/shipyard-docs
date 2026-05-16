```{toctree}
:maxdepth: 2
:caption: 목차
:hidden:

self
02_modbus_signals
03_bitfields_enums
04_errors_alarms
05_ur_appendix
06_ur_dashboard
07_arc_sensing
```

# 1. 개요

이 문서는 조선소 UR 용접 시스템의 통신 프로토콜 메뉴얼 입니다.  
## 1.1 목적

- 펜던트, 로봇, 용접기 사이의 Modbus TCP 주소를 한 곳에서 관리

## 1.2 시스템 구성

```{figure} _static/images/system_architecture.png
---
width: 100%
alt: 시스템 구조(UR / Polyscope / Pendant / Power Source / Wire Feeder)
---
시스템 구조 개요(External Pendant ↔ Polyscope/UR ↔ Power Source/Wire Feeder)
```

```{figure} _static/images/hardware_overview.png
---
width: 90%
alt: 하드웨어 개요(캐비닛, 로봇 컨트롤러, 팬던트, 토치/와이어피더)
---
하드웨어 구성
```

> 프로그램/URSCRIPT 상세 흐름은 5장(UR 컨트롤러 부록)에 추가로 수록했습니다.

## 1.3 시스템 / 프로그램 구조

아래 다이어그램은 URSCRIPT/폴리스코프 중심으로 구성된 통신 개요 및 프로그램 흐름을 요약한 참고 자료입니다.

```{figure} _static/images/program_structure_detail.png
---
width: 100%
alt: URSCRIPT/폴리스코프 중심 프로그램 구조(상세)
---
URSCRIPT/폴리스코프 중심 프로그램 구조(상세)
```

## 1.4 통신 인터페이스 사양(요약)

| 항목 | 값 |
| --- | --- |
| 물리 계층 | Ethernet |
| 프로토콜 | Modbus TCP |
| 전송 속도 | 10Mbps / 100Mbps |
| 통신 방식 | 로봇 Server / 팬던트 & 용접기 Client |
| 기본 Port | 502 |
| 기본 IP  | Hi-COMM 192.168.1.2 / UR 192.168.1.7  / Pendant 192.168.1.207 |

## 1.5 주소 대분류

| 범위 | 방향 / 범주 | 내용 |
| --- | --- | --- |
| 128~160 | 로봇 → 팬던트 | 용접 진행 상태, 셀 정보, 터치 상태, 버전 |
| 161~199 | 팬던트 → 로봇 | 작업 준비, 셀/치수 입력, 옵션/보정값 |
| 201~210 | 로봇 → 용접기 | 용접기 사용, 제어, 전류/전압 설정 |
| 211~220 | 용접기 → 로봇 | 피드백, 오류, 용접 파라미터 |
| 221~255 | 팬던트 → 로봇 | 용접 조건 세트 |
| 0~33, 128~255, 256~ | UR 모드버스 서버 | UR 상태 정보 (5장) |

## 1.6 문서 구성

- **2장**: Modbus 신호 정리
- **3장**: 비트필드 / 열거형
- **4장**: 에러 / 알람
- **5장**: UR 컨트롤러 부록
- **6장**: UR Dashboard Server (원격 명령) / 안전·보호정지 복구 로직
- **7장**: 아크센싱 (개요 / 데이터 수집 / X·Z 보정)
