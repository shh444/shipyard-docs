# 5. UR 컨트롤러 부록

이 장은 **UR Controller(Modbus Server)**가 제공하는 기본 신호(Registers / Coils)를 정리한 부록입니다.

- 본 장의 주소/설명은 **ModBus Server Data** 문서를 기준으로 정리했습니다.
- 표에 없는 상세 제약(컨트롤러 버전별 지원 여부, 정확한 R/W 권한)은 ModBus Server Data 원문을 우선합니다.

원문(PDF):
- [UR Modbus Server Data (PDF)](_static/files/modbus_server_data.pdf)


## 5.1 UR Modbus Register Address (16-bit)

- Register 주소는 **16-bit(0~65535)** 정수 기반입니다.
- 디지털 입력/출력은 bit-pack 형태로 표현되며, 별도의 Coil 영역도 제공합니다(5.2).

### 0~33 : I/O / Analog / Tool / Euromap / Configurable

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 0 | Inputs, bits 0~15 | bit-pack | [BBBBBBBBTTxxxxxx] | x=undef, T=tool, B=box | (R) 입력 비트 패킹 |
| 1 | Outputs, bits 0~15 | bit-pack | [BBBBBBBBTTxxxxxx] | x=undef, T=tool, B=box | (R/W) 출력 비트 패킹 |
| 2 | SetOutputsBitsMask 0~15 | bit mask | [BBBBBBBBTTxxxxxx] | Output 비트 set 마스크 | 주로 (W) 용도 |
| 3 | ClearOutputsBitsMask 0~15 | bit mask | [BBBBBBBBTTxxxxxx] | Output 비트 clear 마스크 | 주로 (W) 용도 |
| 4 | Analog input 0 | 0~65535 | - | 아날로그 입력 0 | 도메인은 5번 |
| 5 | Analog input 0 domain | enum | 0=current(mA), 1=voltage(mV) | 아날로그 입력 0 도메인 | - |
| 6 | Analog input 1 | 0~65535 | - | 아날로그 입력 1 | 도메인은 7번 |
| 7 | Analog input 1 domain | enum | 0=current(mA), 1=voltage(mV) | 아날로그 입력 1 도메인 | - |
| 8 | Analog input 2 (tool) | 0~65535 | - | 툴 아날로그 입력 2 | 도메인은 9번 |
| 9 | Analog input 2 domain | enum | 0=current(mA), 1=voltage(mV) | 툴 아날로그 입력 2 도메인 | - |
| 10 | Analog input 3 (tool) | 0~65535 | - | 툴 아날로그 입력 3 | 도메인은 11번 |
| 11 | Analog input 3 range/domain | enum | 0=current(mA), 1=voltage(mV) | 툴 아날로그 입력 3 도메인 | - |
| 16 | Analog output 0 output | 0~65535 | - | 아날로그 출력 0 | 도메인은 17번 |
| 17 | Analog output 0 domain | enum | 0=current(mA), 1=voltage(mV) | 아날로그 출력 0 도메인 | - |
| 18 | Analog output 1 output | 0~65535 | - | 아날로그 출력 1 | 도메인은 19번 |
| 19 | Analog output 1 domain | enum | 0=current(mA), 1=voltage(mV) | 아날로그 출력 1 도메인 | - |
| 20 | Tool output voltage | enum | 0V / 12V / 24V | 툴 출력 전압 설정/상태 | - |
| 21 | Tool digital input bits | bitfield | - | 툴 디지털 입력 비트 | - |
| 22 | Tool digital output bits | bitfield | - | 툴 디지털 출력 비트 | - |
| 24 | Euromap67 input bits (0~15) | bitfield | - | Euromap67 입력 비트(0~15) | - |
| 25 | Euromap67 input bits (16~32) | bitfield | - | Euromap67 입력 비트(16~32) | - |
| 26 | Euromap67 output bits (0~15) | bitfield | - | Euromap67 출력 비트(0~15) | read only |
| 27 | Euromap67 output bits (16~32) | bitfield | - | Euromap67 출력 비트(16~32) | read only |
| 28 | Euromap 24V voltage | - | - | Euromap 24V 전압 | - |
| 29 | Euromap 24V current | - | - | Euromap 24V 전류 | - |
| 30 | Configurable inputs | bitfield | [BBBBBBBBxxxxxxxx] | 설정 가능한 입력 비트 | - |
| 31 | Configurable outputs | bitfield | [BBBBBBBBxxxxxxxx] | 설정 가능한 출력 비트 | - |
| 32 | Bit mask configurable outputs | bit mask | [BBBBBBBBxxxxxxxx] | configurable output set 마스크 | - |
| 33 | Clear configurable outputs | bit mask | [BBBBBBBBxxxxxxxx] | configurable output clear 마스크 | - |

### 34~127 : Reserved

- 시스템 예약 영역(Reserved for future system variables)

### 128~255 : General purpose 16-bit registers

| 범위 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| --- | --- | --- | --- | --- | --- |
| 128~255 | General purpose 16-bit registers | uint16 | - | 범용 레지스터(사용자 정의 데이터) | 일반적으로 R/W |

### 256~266 : Robot state

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 256 | Controller version high number | - | - | UR 컨트롤러 버전 상위 | - |
| 257 | Controller version low number | - | - | UR 컨트롤러 버전 하위 | - |
| 258 | Robot mode | enum | 0~7 | 로봇 모드(3장 참고) | - |
| 260 | isPowerOnRobot | bool | 0/1 | 로봇 전원 인가 상태 | - |
| 261 | isProtective/SecurityStopped | bool | 0/1 | Protective stop(Security stop) 상태 | 문서 버전에 따라 명칭 상이 |
| 262 | isEmergencyStopped | bool | 0/1 | 비상정지 상태 | - |
| 263 | isTeachButtonPressed | bool | 0/1 | Teach 버튼 눌림 상태 | - |
| 264 | isPowerButtonPressed | bool | 0/1 | Power 버튼 눌림 상태 | - |
| 265 | isSafetySignalSuchThatWeShouldStop | bool | 0/1 | 안전 신호로 인해 정지해야 하는 상태 | - |
| 266 | SafetyMode | enum | - | SafetyMode(Primary Interface manual 참조) | - |

### 270~325 : Joint state

#### 270~275 : Joint angle

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 270 | Base joint angle | mrad | - | 1번 관절 각도 | - |
| 271 | Shoulder joint angle | mrad | - | 2번 관절 각도 | - |
| 272 | Elbow joint angle | mrad | - | 3번 관절 각도 | - |
| 273 | Wrist1 joint angle | mrad | - | 4번 관절 각도 | - |
| 274 | Wrist2 joint angle | mrad | - | 5번 관절 각도 | - |
| 275 | Wrist3 joint angle | mrad | - | 6번 관절 각도 | - |

#### 280~285 : Joint velocity

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 280 | Base joint angle velocity | mrad/s | - | 1번 관절 속도 | - |
| 281 | Shoulder joint angle velocity | mrad/s | - | 2번 관절 속도 | - |
| 282 | Elbow joint angle velocity | mrad/s | - | 3번 관절 속도 | - |
| 283 | Wrist1 joint angle velocity | mrad/s | - | 4번 관절 속도 | - |
| 284 | Wrist2 joint angle velocity | mrad/s | - | 5번 관절 속도 | - |
| 285 | Wrist3 joint angle velocity | mrad/s | - | 6번 관절 속도 | - |

#### 290~295 : Joint current

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 290 | Base joint current | mA | - | 1번 관절 전류 | - |
| 291 | Shoulder joint current | mA | - | 2번 관절 전류 | - |
| 292 | Elbow joint current | mA | - | 3번 관절 전류 | - |
| 293 | Wrist1 joint current | mA | - | 4번 관절 전류 | - |
| 294 | Wrist2 joint current | mA | - | 5번 관절 전류 | - |
| 295 | Wrist3 joint current | mA | - | 6번 관절 전류 | - |

#### 300~305 : Joint temperature

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 300 | Base joint temperature | C | - | 1번 관절 온도 | - |
| 301 | Shoulder joint temperature | C | - | 2번 관절 온도 | - |
| 302 | Elbow joint temperature | C | - | 3번 관절 온도 | - |
| 303 | Wrist1 joint temperature | C | - | 4번 관절 온도 | - |
| 304 | Wrist2 joint temperature | C | - | 5번 관절 온도 | - |
| 305 | Wrist3 joint temperature | C | - | 6번 관절 온도 | - |

#### 310~315 : Joint mode

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 310 | Base joint mode | enum | 236~255 등 | 1번 관절 모드 | 상세 코드는 아래 참조 |
| 311 | Shoulder joint mode | enum | 236~255 등 | 2번 관절 모드 | - |
| 312 | Elbow joint mode | enum | 236~255 등 | 3번 관절 모드 | - |
| 313 | Wrist1 joint mode | enum | 236~255 등 | 4번 관절 모드 | - |
| 314 | Wrist2 joint mode | enum | 236~255 등 | 5번 관절 모드 | - |
| 315 | Wrist3 joint mode | enum | 236~255 등 | 6번 관절 모드 | - |

**Joint mode 코드(문서 발췌)**

- 236: JOINT_SHUTTING_DOWN_MODE
- 237: JOINT_PART_D_CALIBRATION_MODE
- 238: JOINT_BACKDRIVE_MODE
- 239: JOINT_POWER_OFF_MODE
- 245: JOINT_NOT_RESPONDING_MODE
- 246: JOINT_MOTOR_INITIALISATION_MODE
- 247: JOINT_BOOTING_MODE
- 248: JOINT_PART_D_CALIBRATION_ERROR_MODE
- 249: JOINT_BOOTLOADER_MODE
- 250: JOINT_CALIBRATION_MODE
- 252: JOINT_FAULT_MODE
- 253: JOINT_RUNNING_MODE
- 255: JOINT_IDLE_MODE

#### 320~325 : Joint revolution count

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 320 | Base joint revolution count | turns | 0/1 | 관절 회전수(Full turns) | - |
| 321 | Shoulder joint revolution count | turns | 0/1 | 관절 회전수(Full turns) | - |
| 322 | Elbow joint revolution count | turns | 0/1 | 관절 회전수(Full turns) | - |
| 323 | Wrist1 joint revolution count | turns | 0/1 | 관절 회전수(Full turns) | - |
| 324 | Wrist2 joint revolution count | turns | 0/1 | 관절 회전수(Full turns) | - |
| 325 | Wrist3 joint revolution count | turns | 0/1 | 관절 회전수(Full turns) | - |

### 400~451 : TCP / Current

#### 400~405 : TCP pose (base frame)

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 400 | TCP-x | 0.1 mm | - | TCP X (base frame) | tenth of mm |
| 401 | TCP-y | 0.1 mm | - | TCP Y (base frame) | tenth of mm |
| 402 | TCP-z | 0.1 mm | - | TCP Z (base frame) | tenth of mm |
| 403 | TCP-rx | mrad | - | TCP RX (base frame) | - |
| 404 | TCP-ry | mrad | - | TCP RY (base frame) | - |
| 405 | TCP-rz | mrad | - | TCP RZ (base frame) | - |

#### 410~415 : TCP speed (base frame)

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 410 | TCP-x speed | mm/s | - | TCP X 속도 | - |
| 411 | TCP-y speed | mm/s | - | TCP Y 속도 | - |
| 412 | TCP-z speed | mm/s | - | TCP Z 속도 | - |
| 413 | TCP-rx speed | mrad/s | - | TCP RX 속도 | - |
| 414 | TCP-ry speed | mrad/s | - | TCP RY 속도 | - |
| 415 | TCP-rz speed | mrad/s | - | TCP RZ 속도 | - |

#### 420~425 : TCP offset (tool frame)

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 420 | TCP-x offset | mm | - | TCP X 오프셋(tool frame) | - |
| 421 | TCP-y offset | mm | - | TCP Y 오프셋(tool frame) | - |
| 422 | TCP-z offset | mm | - | TCP Z 오프셋(tool frame) | - |
| 423 | TCP-rx offset | mrad | - | TCP RX 오프셋(tool frame) | - |
| 424 | TCP-ry offset | mrad | - | TCP RY 오프셋(tool frame) | - |
| 425 | TCP-rz offset | mrad | - | TCP RZ 오프셋(tool frame) | - |

#### 450~451 : Current

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 450 | Robot current | mA | - | 로봇 전체 전류 | - |
| 451 | I/O current | mA | - | I/O 전류 | - |

### 768~770 : Tool states

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 768 | Tool Mode | enum | - | Tool Mode(Primary Interface manual 참조) | - |
| 769 | Tool temperature | C | - | Tool 온도 | - |
| 770 | Tool current | mA | - | Tool 전류 | - |

### 2048~2053 : RTMachine time

| 주소 | 신호명 | 값/단위 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- | --- |
| 2048 | Split time | trigger | - | 2049~2053에 시간값 latch | 컨트롤러 재시작 이후 시간 |
| 2049 | Milliseconds | ms | - | 밀리초 | - |
| 2050 | Seconds | s | - | 초 | - |
| 2051 | Minutes | min | - | 분 | - |
| 2052 | Hours | h | - | 시 | - |
| 2053 | Days | day | - | 일 | - |

## 5.2 UR Modbus Coil Address (boolean)

Coil 주소는 **boolean(bit)** 영역이며, 아래 범위/신호를 제공합니다.

### Coil 주소 범위

| 범위 | 신호명 | 예시 | 설명 | 비고 |
| --- | --- | --- | --- | --- |
| 0~15 | Inputs bits 0~15 | - | 디지털 입력 비트 | - |
| 16~31 | Outputs bits 0~15 | - | 디지털 출력 비트 | - |
| 32~47 | SetOutputsBitsMask 0~15 | - | 출력 set 마스크 | - |
| 48~63 | ClearOutputsBitsMask 0~15 | - | 출력 clear 마스크 | - |
| 64~79 | Euromap67 input bits (0~15) | - | Euromap 입력 비트 | - |
| 80~95 | Euromap67 input bits (16~32) | - | Euromap 입력 비트 | - |
| 96~111 | Euromap67 output bits (0~15) | - | Euromap 출력 비트 | read only |
| 112~127 | Euromap67 output bits (16~32) | - | Euromap 출력 비트 | read only |
| 128~135 | Configurable inputs | - | 설정 가능한 입력 비트 | - |
| 136~143 | Configurable outputs | - | 설정 가능한 출력 비트 | - |
| 144~151 | Bit mask configurable outputs | - | configurable output set 마스크 | - |
| 152~159 | Clear configurable outputs | - | configurable output clear 마스크 | - |
| 300~427 | GP input boolean registers | - | 128개 범용 입력 boolean 레지스터(RTDE boolean 공유) | - |
| 500~627 | GP output boolean registers | - | 128개 범용 출력 boolean 레지스터(RTDE boolean 공유) | - |

### Coil 단일 신호(상태)

| 주소 | 신호명 | 예시 | 설명 | 비고 |
| ---: | --- | --- | --- | --- |
| 260 | isPowerOnRobot | 0/1 | 로봇 전원 인가 상태 | - |
| 261 | isProtectiveStopped | 0/1 | Protective stop 상태 | - |
| 262 | isEmergencyStopped | 0/1 | 비상정지 상태 | - |
| 263 | isTeachButtonPressed | 0/1 | Teach 버튼 눌림 상태 | - |
| 264 | isPowerButtonPressed | 0/1 | Power 버튼 눌림 상태 | - |
| 265 | isSafetySignalSuchThatWeShouldStop | 0/1 | 안전 신호로 인해 정지해야 하는 상태 | - |
