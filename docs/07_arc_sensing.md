# 7. 아크센싱

이 장은 용접 토치가 모재에 대해 자동으로 위치를 보정할 수 있도록 하는 **아크센싱(Arc Sensing)** 기능을 정리합니다.

용접 중 발생하는 전류 값을 직접 활용하기 때문에 별도의 비전 / 레이저 센서 없이도 동작하며, 위빙(weaving) 동작과 함께 사용해 횡방향(X) 중심 추적과 종방향(Z) 스틱아웃(stick-out) 보정을 수행합니다.

## 7.1 개요

대부분의 산업용 GMAW 용접기는 **CV(Constant Voltage, 정전압) 특성**으로 동작합니다. CV 용접기에서는 전압이 거의 일정하게 유지되는 대신, **아크 길이(= 컨택트 팁 ~ 모재 사이의 거리)** 가 변하면 그에 따라 **전류 값이 변동**합니다.

```{figure} _static/images/welding_wire_distance_current.svg
---
width: 80%
alt: 와이어-모재 거리 변화에 따른 용접 전류 변화 (CV 용접기)
---
```

| 토치–모재 거리 | 아크 길이 | 전류 | 비고 |
| --- | --- | --- | --- |
| 가까워짐 | 짧아짐 | **증가** | 와이어 용융이 빨라져 전류가 커짐 |
| 멀어짐 | 길어짐 | **감소** | 와이어 용융이 느려져 전류가 작아짐 |

이 단순한 원리를 이용해, **위빙으로 토치를 좌우로 흔들면서 각 위치에서 측정된 전류 값을 비교**하면 다음을 알 수 있습니다.

- 위빙 좌/우 끝점의 전류 평균이 다르다 → **중심이 한쪽으로 치우쳐 있음** → 가로(X) 보정 필요
- 위빙 중심점의 전류 평균이 기준보다 높거나 낮다 → **스틱아웃이 짧거나 김** → 세로(Z) 보정 필요

따라서 아크센싱의 핵심은 다음과 같이 정리됩니다.

1. **위빙으로 토치 위치를  변화할 때**,
2. **상하 주기에서의 전류를 측정·누적**해 평균(또는 그에 준하는 통계량)을 구한 뒤,
3. 좌/우 평균 차이로 **X 보정**, 기준값과 평균값을 바탕으로 **Z 보정**을 수행한다.

## 7.2 데이터 수집

아크센싱은 결국 **양질의 전류 데이터를 얼마나 안정적으로 수집하느냐**가 성능을 결정합니다.
본 시스템은 아래 `CalThread()` 스레드에서 일정 주기로 전류/전압을 읽어와 필터링하고, 위빙 방향에 따라 누적합니다.

### 7.2.1 신호 입력 방식

용접기로부터 전류/전압 피드백을 받는 방법은 크게 두 가지입니다.

- **Modbus 신호로 받는 경우** : 용접기에서 이미 정규화된 값이 전달되므로, 스케일만 맞춰서 바로 사용 가능. 노이즈가 없는 것이 장점이지만 통신 지연이 있을 수 있음.
- **아날로그 입력으로 받는 경우(본 코드)** : `get_standard_analog_in()` 으로 0 ~ 1 범위의 정규화 값을 읽은 뒤, **용접기 출력 사양표를 참고해 환산식**을 직접 만들어야 합니다.

본 코드에서는 다음과 같이 환산하고 있습니다.

```python
FB_CURRENT_UR = get_standard_analog_in(1) * 100   # 전류 [A]
FB_VOLTAGE_UR = get_standard_analog_in(0) * 8     # 전압 [V]
```

> 계수 `100`, `8` 은 사용 중인 용접기 모델의 아날로그 출력 사양에 맞춘 값이며, 용접기 모델이 바뀌면 반드시 다시 산정해야 합니다.

읽어온 값은 곧바로 RTDE GP 영역과 Modbus 포트 레지스터에 동시에 기록해 두어, 다른 스레드(보정 로직, 팬던트 모니터링 등)가 같은 값을 공유할 수 있도록 합니다.

```python
# RTDE General Purpose Float Register
write_output_float_register(2, FB_CURRENT_UR)
write_output_float_register(3, FB_VOLTAGE_UR)

# Modbus 포트 레지스터 (2장 131, 132번 참조)
write_port_register(131, FB_CURRENT_UR)
write_port_register(132, FB_VOLTAGE_UR * 10)   # 전압은 0.1V 단위 정수 표기
```

### 7.2.2 HIGH / LOW 필터

용접 시 순간적인 아크 변동(스패터, 단락 직전 피크 등)을 그대로 누적하면 평균값이 크게 흔들립니다.
이를 막기 위해 **상한 `c_maxcut`, 하한 `c_mincut`** 으로 클리핑합니다.

```python
if FB_CURRENT_UR >= c_maxcut and FB_CURRENT_UR > 50:
    FB_CURRENT_UR = c_maxcut
elif FB_CURRENT_UR <= c_mincut and FB_CURRENT_UR > 50:
    FB_CURRENT_UR = c_mincut
```

추가로 **`50A` 이하의 전류는 아크센싱에 사용하지 않습니다.** 무부하·아크 점호 직전·아크 끊김 구간 등 무의미한 데이터를 배제하기 위함입니다.
다만 위 HIGH/LOW 필터가 이미 상/하한을 잡아주기 때문에 `50A` 미만 조건은 실질적으로 호출되지 않습니다(보수적 가드).

### 7.2.3 위빙 방향과 누적 버퍼

본 시스템은 위빙 동작 중 **현재 토치가 위쪽으로 움직이는 반주기인지(`sin_dir = -1`), 아래쪽 반주기인지(`sin_dir = +1`)** 를 별도로 추적하여, 각 방향의 전류를 별도 누적 변수에 저장합니다.

| 변수 | 의미 |
| --- | --- |
| `one_cycle_p_count` | plus 방향(위쪽 반주기) 샘플 개수 |
| `one_cycle_p_accum` | plus 방향 전류 누적합 (필터 적용 후) |
| `one_cycle_p_accum_org` | plus 방향 전류 누적합 (원본, 비교/디버깅용) |
| `one_cycle_m_count` | minus 방향(아래쪽 반주기) 샘플 개수 |
| `one_cycle_m_accum` | minus 방향 전류 누적합 (필터 적용 후) |
| `one_cycle_m_accum_org` | minus 방향 전류 누적합 (원본) |

```python
    if sin_dir == -1:                # plus(위) 반주기
        if peak_value == 100:
            one_cycle_p_count    += 1
            one_cycle_p_accum    += FB_CURRENT_UR
            one_cycle_p_accum_org += FB_CURRENT_UR_org
    else:                            # minus(아래) 반주기
        if peak_value == 100:
            one_cycle_m_count    += 1
            one_cycle_m_accum    += FB_CURRENT_UR
            one_cycle_m_accum_org += FB_CURRENT_UR_org
```

### 7.2.4 `peak_value` 게이트 — 어떤 구간의 전류를 쓸 것인가

`peak_value` 는 **현재 시점의 전류 데이터를 아크센싱 누적에 포함할지 여부**를 결정하는 플래그입니다.
`peak_value == 100` 일 때만 위 누적이 일어나며, 이 값은 다른 스레드 / 메인 루프에서 갱신합니다.

`peak_value` 를 어떻게 켜고 끄느냐에 따라 같은 위빙이라도 아크센싱 성능이 달라집니다. 

대표적인 운용 방식:
- 위빙의 **모서리(끝단)** 구간 데이터만 사용 — 좌/우 차이를 가장 크게 만들어 X 추적 감도 ↑
- 위빙의 **중간 구간**을 제거하고 양 끝만 사용 — 중심부의 흔들림을 배제
- 전 구간을 사용하되 다른 식으로 가중치를 줌

> 본 프로젝트에서는 버전마다 `peak_value` 사용 정책이 달라져 왔습니다. 어떤 구간을 쓸지는 **논문 / 실험 / 경험**에 근거해 결정하고, 그 정책에 맞춰 `peak_value` 가 `100` 이 되는 시점을 별도로 코딩합니다.

### 7.2.5 누적 데이터 활용 방식

누적한 값을 어떻게 통계량으로 변환할지에도 선택지가 있습니다.

1. **단순 평균** (`accum / count`) — 본 시스템 채택. 구현이 단순하고 성능이 안정적.
2. **에너지값 사용** (`I × V` 누적) — 전압 변동까지 함께 반영.
3. **이동 평균** — 노이즈에 더 강하지만 응답이 느려짐.

> 경험적으로 단순 평균이 가장 무난했으나, 테스트에 큰 시간 투자를 안했어서 추가 검토 여지가 있습니다.

### 7.2.6 전체 스레드 골격

```python
thread CalThread():
    while True:
        # --- 1) 전류/전압 읽기 + 환산 ---
        FB_CURRENT_UR = get_standard_analog_in(1) * 100
        FB_VOLTAGE_UR = get_standard_analog_in(0) * 8

        # RTDE / Modbus 공유
        write_output_float_register(2, FB_CURRENT_UR)
        write_output_float_register(3, FB_VOLTAGE_UR)
        write_port_register(131, FB_CURRENT_UR)
        write_port_register(132, FB_VOLTAGE_UR * 10)

        # --- 2) HIGH / LOW 필터 ---
        if FB_CURRENT_UR >= c_maxcut and FB_CURRENT_UR > 50:
            FB_CURRENT_UR = c_maxcut
        elif FB_CURRENT_UR <= c_mincut and FB_CURRENT_UR > 50:
            FB_CURRENT_UR = c_mincut
        end

        # --- 3) 위빙 방향별 누적 (peak_value == 100 구간만) ---
        if FB_CURRENT_UR > 50:
            if current_on == False:
                current_on = True
            end
            if sin_dir == -1:
                if peak_value == 100:
                    one_cycle_p_count     = one_cycle_p_count + 1
                    one_cycle_p_accum     = one_cycle_p_accum + FB_CURRENT_UR
                    one_cycle_p_accum_org = one_cycle_p_accum_org + FB_CURRENT_UR_org
                end
            else:
                if peak_value == 100:
                    one_cycle_m_count     = one_cycle_m_count + 1
                    one_cycle_m_accum     = one_cycle_m_accum + FB_CURRENT_UR
                    one_cycle_m_accum_org = one_cycle_m_accum_org + FB_CURRENT_UR_org
                end
            end
        end

        # --- 4) 같은 시점의 TCP 위치(용접 좌표계 기준) 저장 ---
        GCP = get_feature_pose(get_actual_tcp_pose(), wv_Line_Feature2)
        write_output_float_register(14, GCP[0] * 1000)
        write_output_float_register(15, GCP[1] * 1000)
        write_output_float_register(16, GCP[2] * 1000)
    end
end
```

## 7.3 X 아크센싱 (센터 찾기)

7.2 에서 한 사이클이 끝나면 위빙 **plus 방향(위) 평균 전류 `cycle1_plus`** 와 **minus 방향(아래) 평균 전류 `cycle1_minus`** 두 값이 산출됩니다.
이 두 값의 **차이**가 곧 “용접선 중심에서 토치가 어느 쪽으로 얼마나 치우쳐 있는지”에 대한 정보입니다.

> 이번 절의 계산은 `diff_Thread` 스레드 안에서 수행됩니다.
> X 보정 계산은 **위빙 한 사이클이 끝난 시점에 1회만** 일어납니다.
> `diff_Thread` 는 한 사이클 누적이 끝났음을 감지해 아래 로직을 실행합니다.

```
cycle1_plus > cycle1_minus  →  위쪽 반주기에서 모재에 더 가까웠음  →  중심이 위쪽으로 치우침
cycle1_plus < cycle1_minus  →  아래쪽 반주기에서 모재에 더 가까웠음 →  중심이 아래쪽으로 치우침
```

본 시스템은 이 차이값을 **PI 제어**의 입력으로 받아 한 사이클마다 토치의 가로(X) 오프셋을 갱신합니다.

### 7.3.1 보정 조건 게이트 (언제 적용)

먼저, 아래 두 조건을 **모두 만족할 때만** X 보정을 수행합니다.

```python
if (norm(cycle1_plus - cycle1_minus) > 0.2)
   and cycle1_plus  > (current_to_welding_m - 40)
   and cycle1_minus > (current_to_welding_m - 40):
```

| 조건 | 의미 | 왜 필요한가 |
| --- | --- | --- |
| `norm(plus - minus) > 0.2` | 양/음 반주기 전류차가 의미 있는 크기 | 노이즈 수준의 차이까지 반응하면 모션이 불안정 |
| `plus  > 지령전류 - 40` | plus 반주기 의미 있는 전류차 | 아크가 불안정 전류는 신뢰할 수 없음 |
| `minus > 지령전류 - 40` | minus 반주기 의미 있는 전류차 | 위와 동일 |


### 7.3.2 전류차 → 적응형 게인

위빙 1회 이후 Plus/Minus 차이값의 **크기에 따라 PI 게인을 단계적으로 증폭**합니다.

```python
arc_sensing_diff = cycle1_plus - cycle1_minus

if   norm(arc_sensing_diff) > 12:   # 많이 치우침
    p_gain_u = th_arc_sen[1] / 100  * 2
    i_gain_u = th_arc_sen[2] / 1000 * 2
elif norm(arc_sensing_diff) > 7:    # 중간
    p_gain_u = th_arc_sen[1] / 100  * 1.5
    i_gain_u = th_arc_sen[2] / 1000 * 1.5
else:                               # 거의 중심
    p_gain_u = th_arc_sen[1] / 100
    i_gain_u = th_arc_sen[2] / 1000
```

| `arc_sensing_diff` | 해석 | 게인 배율 | 의도 |
| ---: | --- | ---: | --- |
| `> 12 A` | 중심에서 멀리 떨어짐 | **×2** | 빠르게 중심 쪽으로 복귀 |
| `7 ~ 12 A` | 약간 치우침 | **×1.5** | 적당한 속도로 보정 |
| `≤ 7 A` | 거의 중심 | **×1** | 미세 보정만, 떨림 방지 |



### 7.3.3 입력 안전 필터 — 차이값 클리핑

게인을 곱하기 전, **`arc_sensing_diff` 자체도 ±10 으로 클리핑**합니다.

```python
if   arc_sensing_diff >  10:  arc_sensing_diff =  10
elif arc_sensing_diff < -10:  arc_sensing_diff = -10
```

순간적으로 한 사이클의 전류가 크게 튀는 경우(아크 끊김 직후, 갑작스런 스패터 등)에도 보정량이 과도하게 커지지 않도록 보정 합니다.

### 7.3.4 PI 제어

전류차에 대해 ** PI 제어**를 수행합니다.

```python
Ts     = 1 / system_bus_ms          # 샘플링 주기

Up     = arc_sensing_diff * p_gain_u
Ui     = Ui + arc_sensing_diff * i_gain_u * Ts
Pi_sum = Up + Ui
```

| 항 | 역할 |
| --- | --- |
| `Up` (비례, P) | **현재 전류차**에 비례 — 빠른 반응, 정상 상태 오차 잔존 |
| `Ui` (적분, I) | **누적된 전류차**에 비례 — 잔존 오차 제거, 느린 수렴 |
| `Pi_sum` | 두 항의 합. 이번 사이클의 **최종 이동량 후보** |

> 본 시스템은 D(미분) 항을 사용하지 않습니다. 초기에 넣었다가 큰 성능차이가 없어서 제거 했습니다.

### 7.3.5 출력 안전 필터 — 이동거리 무효화

PI 출력이 한 사이클에 ±7 mm 를 넘는다면, **클리핑이 아니라 0으로 폐기**합니다.

```python
if   Pi_sum >  7:  Pi_sum = 0
elif Pi_sum < -7:  Pi_sum = 0
```

- 7 mm 보다 큰 값이 한 번에 나오면 너무 급격하게 움직여 다음 아크센싱이 정상적으로 되지 않습니다. (양쪽 비교를 하는데 차이가 너무 큼)
- 이런 사이클에서는 보정을 “하지 않는다”가 가장 안전합니다. 그래서 단순 클리핑(`±7`로 자르기)보다 **이번 사이클 반영을 하지 않는** 쪽을 택했습니다.

### 7.3.6 좌표계 반영

최종적으로 `Pi_sum` 에 **아크센싱 사용 여부 스위치(`arc_sens_onoff`)** 를 곱한 값을 이번 사이클의 X 오프셋으로 사용합니다.

```python
arc_x_off = Pi_sum * arc_sens_onoff

if th_par_2f == False:
    th_wv_wp2 = feature_offset(
        th_wv_wp2,
        p[0, -arc_x_off / 1000, 0, 0, 0, 0],   # mm → m, Y 축 방향
        wv_Line_Feature2,
    )
end
```

- `feature_offset` 은 **용접 라인 기준 좌표계(`wv_Line_Feature2`)** 에서 오프셋을 적용합니다. 위빙 평면상에서 “용접선에 수직인 가로 방향”이 곧 이 좌표계의 Y 축입니다.
- `arc_x_off` 단위는 mm 이므로 `/1000` 으로 m 변환.
- Y 부호가 음수(`-arc_x_off`)인 이유는 **`cycle1_plus > cycle1_minus` 일 때(위쪽이 더 가까울 때) 토치를 그 반대편으로 보내야 다시 중심으로 오기 때문**입니다. 기구학적 정의에 따라 부호 규약은 사이트별로 다를 수 있으니, 최초 셋업 시 한 번 검증한 뒤 고정해 두면 됩니다.

> **2F 예외**: `th_par_2f` 가 True 인 경우(2F 멀티패스 일부 버전)에는 X 보정을 반영하지 않습니다. 2F 에서는 위빙 양쪽 끝이 서로 다른 모재 면을 향하므로 plus/minus 전류차가 “중심 이탈”이 아니라 “경사 차이”에서 발생합니다 — 이 경우 X 보정을 그대로 적용하면 오히려 토치가 이상한 방향으로 끌려갑니다.

### 7.3.7 RTDE 로그

튜닝과 사후 분석을 위해 P/I/최종 이동량을 로그 레지스터에 남깁니다.

```python
write_output_float_register(10, Up)          # P 항
write_output_float_register(11, Ui)          # I 항
write_output_float_register(4,  -arc_x_off)  # 최종 적용 X 오프셋 [mm]
```

| 레지스터 | 내용 | 활용 |
| ---: | --- | --- |
| `output_float_register[10]` | `Up` | P 게인 튜닝 — 응답 속도가 부족한지 확인 |
| `output_float_register[11]` | `Ui` | I 게인 튜닝 — 정상상태 오차가 남는지 확인 |
| `output_float_register[4]`  | `-arc_x_off` (mm) | 사이클별 실제 이동량, 위빙 진행과 함께 그래프로 보면 수렴 거동이 한눈에 보임 |

### 7.3.8 전체 코드

```python
# ---------------------------- X offset (센터 추적) ----------------------------
if (norm(cycle1_plus - cycle1_minus) > 0.2)
   and cycle1_plus  > (current_to_welding_m - 40)
   and cycle1_minus > (current_to_welding_m - 40):

    arc_sensing_diff = cycle1_plus - cycle1_minus

    # 1) 차이 크기에 따른 적응형 게인
    if norm(arc_sensing_diff) > 12:
        p_gain_u = th_arc_sen[1] / 100  * 2
        i_gain_u = th_arc_sen[2] / 1000 * 2
    elif norm(arc_sensing_diff) > 7:
        p_gain_u = th_arc_sen[1] / 100  * 1.5
        i_gain_u = th_arc_sen[2] / 1000 * 1.5
    else:
        p_gain_u = th_arc_sen[1] / 100
        i_gain_u = th_arc_sen[2] / 1000
    end

    Ts = 1 / system_bus_ms

    # 2) 입력 클리핑
    if   arc_sensing_diff >  10: arc_sensing_diff =  10
    elif arc_sensing_diff < -10: arc_sensing_diff = -10
    end

    # 3) PI 제어
    Up     = arc_sensing_diff * p_gain_u
    Ui     = Ui + arc_sensing_diff * i_gain_u * Ts
    Pi_sum = Up + Ui

    # 4) 출력 보호 (과대 이동량은 무효화)
    if   Pi_sum >  7: Pi_sum = 0
    elif Pi_sum < -7: Pi_sum = 0
    end

    arc_x_off = Pi_sum * arc_sens_onoff

    # 5) 용접 좌표계에 반영 (2F 일부 버전 제외)
    if th_par_2f == False:
        th_wv_wp2 = feature_offset(
            th_wv_wp2,
            p[0, -arc_x_off / 1000, 0, 0, 0, 0],
            wv_Line_Feature2,
        )
    end

    # 6) 로그
    write_output_float_register(10, Up)
    write_output_float_register(11, Ui)
    write_output_float_register(4,  -arc_x_off)
end
```

## 7.4 Z 아크센싱 (스틱아웃 추정)

X 아크센싱이 위빙 좌/우 반주기의 **상대적 차이**를 이용해 중심을 찾았다면, Z 아크센싱은 **사이클 평균 전류의 절대값**을 미리 정해 둔 **기준 전류(`Standard_Arc_Current`)** 와 비교하여 스틱아웃(stick-out) 거리를 보정합니다.

```
cycle1_middle > Standard_Arc_Current  →  실제 전류가 더 큼  →  토치가 모재에 가까움  →  Z 를 띄워야 함
cycle1_middle < Standard_Arc_Current  →  실제 전류가 더 작음 →  토치가 모재에서 멈   →  Z 를 낮춰야 함
```

전반적 흐름은 [7.3](07_arc_sensing.md#7-3-x-아크센싱-센터-찾기) 의 X 보정과 동일하게 PI 제어 기반이며, **입력값의 정의 / 게인 스케일 / 출력 보호 방식**에서 차이가 있습니다.

> 이번 절의 계산도 `diff_Thread` 스레드에서, **위빙 한 사이클이 끝난 시점에 1회** 수행됩니다.

### 7.4.1 기준 전류 `Standard_Arc_Current` — 고정값 사용

Z 보정의 핵심은 “**기준 전류를 얼마로 둘 것인가**” 입니다. 본 시스템은 **지령 전류(`current_to_welding_m`) 대비 고정값**을 `Standard_Arc_Current` 로 사용합니다.

선택지 자체는 두 가지가 있습니다.

1. **지령 전류 기반 고정값** (본 시스템 채택)
   사용자가 지령한 용접 전류에 대응하는 “정상 스틱아웃일 때 기대되는 전류”를 사전에 정해 두고 그 값을 그대로 사용합니다.
2. **초기 N 사이클(3~4 cycle) 평균을 기준값으로 사용**
   터치센싱 등으로 **정확한 스틱아웃이 잡혀 있는 상태**에서 시작할 때, 첫 몇 사이클의 평균 전류를 기준값으로 그대로 쓸 수 있습니다. 원리적으로는 가장 정확합니다.

본 시스템이 (1) 을 택한 이유는, 용접 시작 직후 몇 사이클은 **모따기 / 스패터 / 아크 점호 직후 불안정** 등의 변수가 크게 작용해 평균 전류가 실제 정상 상태를 대표하지 못하는 경우가 많기 때문입니다. 잘못된 기준값이 한 번 잡히면 이후 사이클 전체가 그 기준에 끌려가게 되므로, 본 시스템은 안전하게 **고정값** 으로 운용합니다.

### 7.4.2 보정 조건 게이트

X 와 달리 Z 는 **차이값이 의미 있는 크기일 때만** 보정합니다.

```python
arc_sensing_diff_z = Standard_Arc_Current - cycle1_middle

if norm(arc_sensing_diff_z) > 0.2:
    ...
```

| 조건 | 의미 | 왜 필요한가 |
| --- | --- | --- |
| `norm(Standard - cycle1_middle) > 0.2` | 기준값과 사이클 평균의 차이가 의미 있는 크기 | 노이즈 수준 차이까지 반응하면 Z 가 떨림 |

> X 보정에서 사용했던 “지령전류 - 40 A” 가드는 Z 에서는 사용하지 않습니다. Z 는 절대값 비교가 본질이므로 이미 `Standard_Arc_Current` 자체가 안전 기준 역할을 합니다.

### 7.4.3 전류차 → 적응형 게인

차이의 **크기에 따라 PI 게인을 단계적으로 증폭**합니다. 임계값과 배율이 X 와 다릅니다.

```python
if   norm(arc_sensing_diff_z) > 10:   # 많이 벗어남
    p_gain_u_z = th_arc_sen[3] / 1000 * 3.5
    i_gain_u_z = th_arc_sen[4] / 1000 * 3
elif norm(arc_sensing_diff_z) > 5:    # 중간
    p_gain_u_z = th_arc_sen[3] / 1000 * 1.8
    i_gain_u_z = th_arc_sen[4] / 1000 * 1.5
else:                                 # 거의 기준값에 근접
    p_gain_u_z = th_arc_sen[3] / 1000
    i_gain_u_z = th_arc_sen[4] / 1000
```

| `arc_sensing_diff_z` | 해석 | 게인 배율 (P / I) | 의도 |
| ---: | --- | ---: | --- |
| `> 10 A` | 기준 스틱아웃에서 크게 벗어남 | **×3.5 / ×3** | 빠르게 정상 거리로 복귀 |
| `5 ~ 10 A` | 약간 벗어남 | **×1.8 / ×1.5** | 적당한 속도로 보정 |
| `≤ 5 A` | 기준에 근접 | **×1 / ×1** | 미세 보정만, 떨림 방지 |

> X 에서 P 게인 분모가 `100` 이었던 것과 달리, Z 는 `1000` 입니다. 같은 `th_arc_sen` 값이라도 Z 가 한 자릿수 더 작은 게인으로 동작하도록 설계되어 있으며, 이는 **스틱아웃 변화가 X 보정만큼 빠르게 움직일 필요가 없기 때문**입니다.

### 7.4.4 입력 안전 필터 — 차이값 클리핑

게인을 곱하기 전, **`arc_sensing_diff_z` 자체를 ±10 으로 클리핑**합니다.

```python
if   arc_sensing_diff_z >  10: arc_sensing_diff_z =  10
elif arc_sensing_diff_z < -10: arc_sensing_diff_z = -10
```

스패터 / 아크 끊김 직후 등으로 한 사이클의 평균 전류가 크게 튀더라도 보정량이 과도해지지 않도록 가드합니다.

### 7.4.5 PI 제어

X 와 동일한 형태의 PI 제어를 별도 적분기 `Ui_z` 로 수행합니다.

```python
Ts       = 1 / system_bus_ms

Up_z     = arc_sensing_diff_z * p_gain_u_z
Ui_z     = Ui_z + arc_sensing_diff_z * i_gain_u_z * Ts
Pi_sum_z = Up_z + Ui_z
```

| 항 | 역할 |
| --- | --- |
| `Up_z` (비례, P) | 현재 사이클의 기준-평균 차이에 비례 |
| `Ui_z` (적분, I) | 누적된 차이에 비례 — 정상상태 오차 제거 |
| `Pi_sum_z` | 이번 사이클의 **최종 Z 이동량 후보** |

> 적분기 `Ui_z` 는 X 의 `Ui` 와 **완전히 분리된 상태 변수** 입니다. X / Z 보정이 서로 간섭하지 않습니다.

### 7.4.6 출력 안전 필터 — 클리핑(폐기 X)

PI 출력이 한 사이클에 ±5 mm 를 넘으면 **그대로 클리핑** 합니다.

```python
if   Pi_sum_z >  5: Pi_sum_z =  5
elif Pi_sum_z < -5: Pi_sum_z = -5
```

X 보정과 다른 점은 다음과 같습니다.

| 축 | 한계 | 초과 시 동작 | 이유 |
| --- | ---: | --- | --- |
| X | ±7 mm | **0 으로 폐기** | X 가 한 번에 크게 이동하면 다음 사이클의 좌/우 비교 자체가 깨짐 — 차라리 이번 사이클을 건너뜀 |
| Z | ±5 mm | **±5 로 클리핑** | Z 는 절대 기준 비교라 다음 사이클에 영향이 적음 — 큰 변화 시점에도 천천히라도 따라가는 편이 안전 |

### 7.4.7 좌표계 반영

최종 `Pi_sum_z` 에 아크센싱 사용 스위치(`arc_sens_onoff`) 를 곱한 값을 이번 사이클의 Z 오프셋으로 사용합니다.

```python
global arc_z_off = Pi_sum_z * arc_sens_onoff

if th_par_2f == False:
    th_wv_wp2 = feature_offset(
        th_wv_wp2,
        p[0, 0, arc_z_off / 1000, 0, 0, 0],   # mm → m, Z 축 방향
        wv_Line_Feature2,
    )
end
```

- `feature_offset` 은 **용접 라인 기준 좌표계(`wv_Line_Feature2`)** 에서 오프셋을 적용합니다. 위빙 평면에 수직인 “스틱아웃 방향”이 곧 이 좌표계의 Z 축입니다.
- `arc_z_off` 단위는 mm 이므로 `/1000` 으로 m 변환.
- X 와 달리 부호를 뒤집지 않습니다. `Standard - cycle1_middle > 0` (실제 전류가 작음 → 토치가 멀어진 상태) 일 때 `arc_z_off` 가 양수가 되어 Z 를 모재 쪽으로 다시 내려보내는 방향이 자연스럽게 잡힙니다. 단, 이 부호 규약은 현장 셋업과 좌표계 정의에 따라 다를 수 있으니 최초 셋업 시 한 번 검증해 두면 됩니다.

> **2F 예외**: `th_par_2f == True` 인 경우(2F 멀티패스 일부 버전) Z 보정도 반영하지 않습니다. 2F 위빙은 좌/우 모재 면이 서로 다른 거리/각도에 있어 사이클 평균 전류 자체가 “스틱아웃”을 대표하지 않게 됩니다.

### 7.4.8 RTDE 로그

X 와 별도의 레지스터에 P / I / 최종 이동량을 기록합니다.

```python
write_output_float_register(12, Up_z)      # P 항
write_output_float_register(13, Ui_z)      # I 항
write_output_float_register(5,  arc_z_off) # 최종 적용 Z 오프셋 [mm]
```

| 레지스터 | 내용 | 활용 |
| ---: | --- | --- |
| `output_float_register[12]` | `Up_z` | P 게인 튜닝 — 스틱아웃 변화에 대한 응답 속도 확인 |
| `output_float_register[13]` | `Ui_z` | I 게인 튜닝 — 정상상태 스틱아웃 오차 확인 |
| `output_float_register[5]`  | `arc_z_off` (mm) | 사이클별 실제 Z 이동량 — X 로그(`[4]`) 와 함께 보면 위빙 한 사이클의 보정 거동을 동시에 추적 가능 |

### 7.4.9 전체 코드

```python
# ---------------------------- Z offset (스틱아웃 추정) ----------------------------
arc_sensing_diff_z = Standard_Arc_Current - cycle1_middle

if norm(arc_sensing_diff_z) > 0.2:

    # 1) 차이 크기에 따른 적응형 게인
    if norm(arc_sensing_diff_z) > 10:
        p_gain_u_z = th_arc_sen[3] / 1000 * 3.5
        i_gain_u_z = th_arc_sen[4] / 1000 * 3
    elif norm(arc_sensing_diff_z) > 5:
        p_gain_u_z = th_arc_sen[3] / 1000 * 1.8
        i_gain_u_z = th_arc_sen[4] / 1000 * 1.5
    else:
        p_gain_u_z = th_arc_sen[3] / 1000
        i_gain_u_z = th_arc_sen[4] / 1000
    end

    Ts = 1 / system_bus_ms

    # 2) 입력 클리핑
    if   arc_sensing_diff_z >  10: arc_sensing_diff_z =  10
    elif arc_sensing_diff_z < -10: arc_sensing_diff_z = -10
    end

    # 3) PI 제어
    Up_z     = arc_sensing_diff_z * p_gain_u_z
    Ui_z     = Ui_z + arc_sensing_diff_z * i_gain_u_z * Ts
    Pi_sum_z = Up_z + Ui_z

    # 4) 출력 클리핑 (X 와 달리 0 폐기 X, 그대로 ±5 로 자름)
    if   Pi_sum_z >  5: Pi_sum_z =  5
    elif Pi_sum_z < -5: Pi_sum_z = -5
    end

    global arc_z_off = Pi_sum_z * arc_sens_onoff

    # 5) 용접 좌표계에 반영 (2F 일부 버전 제외)
    if th_par_2f == False:
        th_wv_wp2 = feature_offset(
            th_wv_wp2,
            p[0, 0, arc_z_off / 1000, 0, 0, 0],
            wv_Line_Feature2,
        )
    end

    # 6) 로그
    write_output_float_register(12, Up_z)
    write_output_float_register(13, Ui_z)
    write_output_float_register(5,  arc_z_off)
end
```
