# UR 컨트롤러 부록

이 페이지는 PDF에 포함된 **UR Native** 주소만 별도로 정리한 부록입니다.

## 기본 상태

| 주소 | 신호 | 값/단위 | 설명 |
| --- | --- | --- | --- |
| 0 | UR Inputs, bit 0~15 | [BBBBBBBBTTxxxxxx] | x=undef, T=tool, B=box |
| 1 | UR Outputs, bit 0~15 | [BBBBBBBBTTxxxxxx] | x=undef, T=tool, B=box |
| 256 | Controller version high number |  | UR 컨트롤러 버전 상위 번호 |
| 258 | Robot Mode | 0/1/2/3/5/6/7 | Disconnected=0, Confirm_safety=1, Booting=2, Power_off=3, Idle=5, Backdrive=6, Running=7 |
| 260 | isPowerOnRobot |  | 로봇 전원 인가 상태 |
| 261 | isSecurityStopped |  | 보호정지 상태 |
| 262 | isEmergencyStopped |  | 비상정지 상태 |
| 265 | isSafetySignalSuchThatWeShouldStop |  | 안전 신호로 인한 정지 |

## 관절 정보

| 범위 | 신호 | 단위 |
| --- | --- | --- |
| 270~275 | Joint 1~6 angle | mrad |
| 280~285 | Joint 1~6 speed | mrad/s |
| 290~295 | Joint 1~6 current | mA |
| 300~305 | Joint 1~6 temp | C |

## 회전수 카운트

| 주소 | 신호 |
| --- | --- |
| 320 | Base joint revolution count |
| 321 | Shoulder joint revolution count |
| 322 | Elbow joint revolution count |
| 323 | Wrist1 joint revolution count |
| 324 | Wrist2 joint revolution count |
| 325 | Wrist3 joint revolution count |

## TCP Pose

| 주소 | 신호 |
| --- | --- |
| 400 | TCP X |
| 401 | TCP Y |
| 402 | TCP Z |
| 403 | TCP RX |
| 404 | TCP RY |
| 405 | TCP RZ |
