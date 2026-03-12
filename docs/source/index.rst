조선소 용접 시스템 Modbus TCP 신호 매뉴얼
===========================================

.. image:: https://img.shields.io/badge/Version-1.0-blue
   :alt: Version 1.0

.. image:: https://img.shields.io/badge/Protocol-Modbus_TCP-green
   :alt: Modbus TCP

본 문서는 조선소 용접 자동화 시스템의 **Modbus TCP 신호 주소 맵**을 정의합니다.

시스템 구성
-----------

* 🤖 **UR 협동로봇** (Universal Robot) - Modbus TCP Slave
* 📱 **용접 제어 펜던트** - 제어 UI
* ⚡ **Hi-COMM Ethernet** - Modbus TCP Master

네트워크 설정
-------------

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - 장치
     - IP 주소
     - 역할
   * - UR 협동로봇
     - 192.168.1.7
     - Modbus TCP Slave (Server)
   * - Hi-COMM Ethernet
     - 192.168.1.2
     - Modbus TCP Master (Client)

통신 사양
---------

* **프로토콜:** Modbus TCP
* **포트:** 502
* **폴링 주기:** 10ms (100Hz)
* **함수 코드:** FC 04 (Read), FC 16 (Write)

주소 범위 요약
--------------

.. list-table::
   :header-rows: 1
   :widths: 15 20 15 50

   * - 범위
     - 통신 방향
     - 레지스터 수
     - 주요 신호
   * - 0~1
     - UR I/O
     - 2
     - Digital Input/Output (Tool, Box)
   * - 128~160
     - 🤖→📱 (로봇→펜던트)
     - 33
     - 하트비트, 용접상태, 전류/전압, PATH 정보
   * - 161~255
     - 📱→🤖 (펜던트→로봇)
     - 95
     - 작업모드, 용접조건, 치수정보, 파라미터
   * - 201~210
     - 🤖→⚡ (로봇→용접기)
     - 10
     - 용접기 제어, 전류/전압 설정
   * - 211~223
     - ⚡→🤖 (용접기→로봇)
     - 13
     - 전류/전압 피드백, 오류코드
   * - 256~405
     - UR 로봇 시스템
     - 150
     - 로봇모드, 조인트, TCP 위치

.. toctree::
   :maxdepth: 2
   :caption: 신호 목록

   modbus_signals

빠른 검색
---------

* :ref:`search`
* :ref:`genindex`
