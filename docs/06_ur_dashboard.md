# 6. UR Dashboard Server

이 장은 **UR Controller의 Dashboard Server**(원격 명령 인터페이스)를 설명합니다.

- Modbus TCP(Port 502)가 *신호(레지스터/코일)* 중심이라면, Dashboard Server는 **Polyscope(GUI)에 텍스트 명령을 보내서 상태를 조회하거나 동작(전원/브레이크/프로그램)을 제어**하는 용도입니다.
- 본 프로젝트에서는 Modbus 신호를 감시하다가 안전/보호정지 등 오류 상황이 발생했을 때, **Dashboard 명령으로 복구 시퀀스**를 수행하는 데 사용합니다.

참고 문서(PDF):
- [Dashboard Server (CB-Series) Commands](_static/files/dashboard_server_cb_series.pdf)

> ⚠️ 안전 주의
>
> Dashboard Server는 안전 팝업 닫기, 보호정지 해제, Safety 재시작 등의 기능을 제공합니다.
> **원인을 확인하고 위험이 제거된 것이 확실할 때만** 실행해야 합니다.
> (예: 작업자 침입/안전센서 동작/비상정지/충돌 원인 등이 남아있는 상태에서 강제 복구를 시도하면 위험합니다.)

---

## 6.1 접속/프로토콜 개요

- **TCP/IP 소켓**으로 UR 컨트롤러에 접속합니다.
- 기본 포트는 **29999** 입니다.
- 명령은 **ASCII 텍스트 + 개행(\n)** 으로 전송합니다.
  - 예: `safetymode\n`, `power on\n`, `brake release\n`
- 명령은 **대소문자를 구분하지 않는** 것으로 알려져 있습니다.

공식 참고(UR):
- [Dashboard Server (CB-Series), port 29999](https://www.universal-robots.com/articles/ur/dashboard-server-cb-series-port-29999/)
- [Dashboard Server (e-Series), port 29999](https://www.universal-robots.com/articles/ur/dashboard-server-e-series-port-29999/)

### (예시) 테스트 접속

- Linux/macOS:

```bash
nc <ROBOT_IP> 29999
# 접속 후 아래와 같이 입력
safetymode
robotmode
```

- Windows(간단 테스트): PuTTY/Telnet 또는 TCP 테스트 툴 사용

---

## 6.2 자주 사용하는 Dashboard 명령

아래 명령들은 **에러 감지/복구 시퀀스**에서 핵심적으로 사용됩니다.

### 상태 조회

- `robotmode` : 로봇 모드 조회
  - 예: `Robotmode: POWER_OFF`, `Robotmode: POWER_ON`, `Robotmode: IDLE`, `Robotmode: RUNNING` 등
- `safetymode` : 안전 모드 조회
  - 예: `Safetymode: NORMAL`, `Safetymode: PROTECTIVE_STOP`, `Safetymode: SAFEGUARD_STOP`, `Safetymode: VIOLATION`, `Safetymode: FAULT` 등

### 안전/복구

- `close safety popup` : 안전 팝업 닫기
- `unlock protective stop` : 보호정지(Protective stop) 해제
  - 보호정지 발생 **5초 이내에는 실패**할 수 있습니다.
- `restart safety` : Safety 재시작
  - Safety fault/violation 등에서 사용합니다.
  - 재시작 후 로봇은 **Power Off 상태**가 됩니다.

### 전원/브레이크

- `power on` : 로봇 암 전원 인가
- `brake release` : 브레이크 해제

---

## 6.3 Modbus 에러 감시 → Dashboard 복구(권장 로직)

아래는 요청하신 **에러 처리 로직(시퀀스)** 을 문서화한 것입니다.

### 6.3.1 트리거(예시)

Modbus 감시 중 아래 중 하나라도 감지되면 복구 루틴을 시작합니다.

- 보호정지/시큐리티 스톱 관련: `261 == 1`
- 비상정지 관련: `262 == 1`
- 안전 신호로 정지해야 하는 상태: `265 == 1`
- 프로젝트 에러 코드(예: 151 하트비트 실패) 발생

> 위 레지스터/코드들은 4장/5장에 정리된 상태 신호를 기준으로 합니다.

---

### 6.3.2 복구 시퀀스(개요)

아래는 프로젝트에서 요청하신 흐름을 기준으로 **문장 그대로** 정리한 시퀀스입니다.

- Modbus 감시 중 에러 감지 → Dashboard `safetymode` 확인
- 보호정지(예: `PROTECTIVE_STOP`)로 판단되면
  1) 보호정지 상태로 간주(원인 확인/로그 기록)
  2) `close safety popup` (안전 팝업 끄기)
  3) 필요 시 `restart safety` (Safety 재시작)
  4) `power on`
  5) 상태(`robotmode` 또는 Modbus `260`)를 보다가 Power On 되면
  6) `brake release`

> 참고: UR 공식 명령 체계에서는 **보호정지(Protective stop) 해제는 `unlock protective stop`** 명령을 제공하며,
> `restart safety`는 주로 **Safety fault/violation** 복구에 사용됩니다.
> 현장 요구에 따라 위 두 가지를 조합할 수 있으나, 어떤 경우든 **원인 제거/안전 확인**이 우선입니다.

1) **Dashboard `safetymode`** 로 현재 안전 상태를 먼저 판별
2) 상태에 따라
   - **PROTECTIVE_STOP** 이면: 안전 팝업 닫기 → (필요 시) 보호정지 해제
   - **FAULT/VIOLATION** 이면: 안전 팝업 닫기 → Safety 재시작
   - **SAFEGUARD_STOP / EMERGENCY_STOP** 이면: 물리적 원인 해소가 먼저(안전센서/비상정지 해제)
3) Safety가 정상화되면
   - `power on`
   - 상태를 보다가(= `robotmode` 또는 Modbus `260`) **POWER_ON** 되면
   - `brake release`

---

### 6.3.3 복구 시퀀스(상세 단계)

아래는 구현 시 바로 적용할 수 있도록 **단계별로** 정리한 권장 절차입니다.

#### Step A) safetymode 확인

- Dashboard로 `safetymode`를 폴링하여 현재 모드를 확인합니다.

판정 예시:
- `Safetymode: PROTECTIVE_STOP` → 보호정지
- `Safetymode: FAULT` 또는 `Safetymode: VIOLATION` → Safety fault/violation
- `Safetymode: SAFEGUARD_STOP` / `SYSTEM_EMERGENCY_STOP` / `ROBOT_EMERGENCY_STOP` → 안전장치/비상정지

#### Step B-1) PROTECTIVE_STOP(보호정지) 처리

1. `close safety popup`
2. 보호정지 발생 직후라면 최소 5초 경과 후
   - `unlock protective stop`
3. 다시 `safetymode`를 확인하여 `NORMAL` 또는 `REDUCED`로 복귀했는지 확인

> 보호정지는 충돌/과부하 등 원인이 있을 수 있으므로, 자동 해제 전에 원인 확인이 필요합니다.

#### Step B-2) FAULT/VIOLATION 처리

1. `close safety popup`
2. `restart safety`
   - 실행 후 로봇은 Power Off가 되므로 다음 단계에서 `power on`이 필요합니다.

> `restart safety`는 안전 시스템을 재부팅하는 동작이므로, **반드시 원인 점검 후** 사용합니다.

#### Step B-3) SAFEGUARD_STOP / EMERGENCY_STOP 처리

- 이 경우에는 대시보드 명령만으로 즉시 복구되지 않을 수 있습니다.
- 현장 조건(안전센서, 라이트커튼, 도어 인터락, e-stop 등)을 먼저 해제한 뒤에
  - `close safety popup`
  - (가능하면) `safetymode`가 정상으로 돌아오는지 확인
  - 이후 Step C 진행

---

#### Step C) Power On → Power On 확인 → Brake Release

1. `power on`
2. 아래 중 하나로 Power On 상태를 확인(폴링)
   - Dashboard: `robotmode`가 `POWER_ON` 또는 `IDLE`
   - Modbus: `260 (isPowerOnRobot) == 1`
3. Power On 확인되면
   - `brake release`
4. 최종적으로
   - `robotmode == IDLE` 또는 Modbus 상 안전 관련 레지스터가 정상인지 확인 후 작업 재개

---

## 6.4 구현 팁(통신/에러 처리)

### 6.4.1 명령 전송/응답 처리

- Dashboard는 명령마다 문자열 응답이 오며, 실패 시에도 실패 메시지가 반환됩니다.
- 예: 프로그램 관련 명령은 `Failed to execute: <command>` 형태로 실패할 수 있습니다.

권장:
- 명령 전송 후 **응답 문자열을 항상 로그로 남기기**
- 기대 응답이 아닐 경우 재시도/중단을 명확히 구분하기

### 6.4.2 타임아웃/재시도

- `unlock protective stop`은 **5초 이내 실행 시 실패**할 수 있으므로
  - 최소 5초 대기 후 1~N회 재시도하는 방식이 안전합니다.
- `restart safety` 이후에는 컨트롤러 내부 재기동 시간이 필요합니다.
  - `robotmode`가 `POWER_OFF`로 안정화될 때까지 폴링 후 다음 단계 진행을 권장합니다.

### 6.4.3 자동 복구의 한계

- 안전장치가 실제로 동작 중이면(비상정지 눌림, 도어 인터락 열림 등)
  - Dashboard 명령이 성공하더라도 로봇이 정상 상태로 돌아오지 않을 수 있습니다.
- 자동 복구는 **“원인이 제거된 뒤, 사람이 승인한 재가동”** 을 전제로 설계하는 것을 권장합니다.

