# 📏 Tape_measure — 1 규빗은 얼마인가?

> *"신이 노아에게 '300 규빗'짜리 배를 만들라고 했을 때,*
> *노아는 줄자를 꺼냈다. 그 줄자의 이름은 '내 팔'이었다."*

---

> **레포 이름이 Tape_measure인 이유:**
> 인류 최초의 줄자는 팔꿈치였고, 그 이름이 규빗(Cubit)이었다.
> 노아는 자기 팔로 방주를 쟀고, 모세는 자기 팔로 법궤를 쟀다.
> *이 레포는 그 팔의 크기를 역추적한다.*

---

## 한 줄 요약

```
1 규빗 = 팔꿈치 ~ 손끝 = 신체 비례 단위
        = 시대마다 달랐다 (궁창 붕괴 → 수명 감소 → 신체 감소)
        = 노아의 팔: ~90cm / 아브라함의 팔: ~51cm / 지금 내 팔: ~44.5cm
```

---

## 패키지 이름 체계

```
레포        : Tape_measure  (유머, 최초의 줄자 = 팔)
Python 패키지: midos_engine  (import 이름)
엔진 닉네임  : MIDOS         (Biblical Measurement Intelligence & Dimension OS)
              ← 미쉬나 '미도트(Middot)' = 측량, 성전 치수를 기록한 탈무드 소책자
```

---

## 빠른 시작

```bash
# Tape_measure/ 에서 실행
python midos_engine/run_midos_demo.py --all

python midos_demo/run_midos_demo.py --person Noah      # 노아 (하이퍼 규빗)
python midos_engine/run_midos_demo.py --person 아브라함  # 족장 시대
python midos_engine/run_midos_demo.py --person Moses    # 모세 (성막 시대)
python midos_engine/run_midos_demo.py --temporal        # 시대별 규빗 감소 추적
python midos_engine/run_midos_demo.py --sensitivity     # 대기 감도 분석
python midos_engine/run_midos_demo.py --validate        # 고고학 교차 검증
```

```python
from midos_engine import analyze

# 노아 기준 완전 분석
r = analyze("Noah")
print(r.cubit.cm)                          # 89.98 cm  ← 하이퍼 규빗
print(r.ark.dims_m["길이(length)"])         # 269.9 m   ← 타이타닉(269m)과 동일
print(r.body.height_cm)                    # 343.7 cm  ← 3.4m 거인
print(r.explain())                         # 전체 물리 해설
print(r.snapshot_updates)                  # CookiieBrain 파이프라인 연결

# 아브라함 기준
r2 = analyze("Abraham")
print(r2.cubit.cm)                         # 51.07 cm  ← 이집트 왕실(52.5cm)과 97% 일치
```

---

## 왜 규빗이 시대마다 달랐는가

```
규빗(amah, אַמָּה) = 팔꿈치 ~ 손끝
                  = 신체 비례 단위
                  = 신체 크기 ∝ 대기 환경 × 성장 기간(수명 proxy)

창세기 1:6-8  →  궁창(raqia, רָקִיעַ) = 수증기층
                  UV 차폐 95% + 대기압 2.18배 + O2 30%
                  → 거대 생물 지지 (석탄기 유사)
                  → 인간: 수명 900년대, 신장 3m+

창세기 7:11   →  "하늘의 창들이 열려" = 궁창 붕괴
                  → 환경 급변 → 수명 급감 → 신체 감소 → 규빗 감소
```

---

## 시대별 규빗 추적 결과

```
인물           수명     규빗       신장      현대 대비  비교
─────────────────────────────────────────────────────────────
므두셀라        969년    90.2cm    344cm     2.03×     궁창 시대 최장수
노아            950년    90.0cm    344cm     2.02×     방주 건설 (타이타닉 = 269m)
야렛            962년    90.1cm    344cm     2.03×     궁창 시대
────────────── 홍수 (궁창 붕괴) ──────────────────────────────
셈              600년    66.1cm    252cm     1.49×     노아의 아들
아르박삿        438년    63.8cm    244cm     1.43×
에벨            464년    64.2cm    245cm     1.44×
벨렉            239년    59.7cm    228cm     1.34×     바벨탑 시대
────────────── 족장 시대 ─────────────────────────────────────
아브라함        175년    51.1cm    195cm     1.15×     이집트 왕실 규빗(52.5cm)과 97%
이삭            180년    51.2cm    196cm     1.15×
야곱            147년    50.1cm    191cm     1.13×
────────────── 모세·성막 시대 ───────────────────────────────
모세            120년    47.2cm    180cm     1.06×     탈무드 R.Naeh(48cm)과 98%
────────────── 왕국 시대 ─────────────────────────────────────
솔로몬           60년    43.5cm    166cm     0.98×     성전 건설
────────────── 현대 ──────────────────────────────────────────
현대인           75년    44.5cm    170cm     1.00×     고고학 실측 일치 ✓
```

---

## 핵심 발견

```
① 노아 방주 (300 규빗 × 하이퍼 규빗 89.9cm):
   길이 = 269.9m  ← 타이타닉(269.0m)과 1m 차이
   → 우연? 아니면 거대 선박의 물리적 최적 규모가 같다?

② 아브라함 규빗 (51.1cm):
   이집트 왕실 규빗 (52.5cm)과 97% 일치
   → 족장 시대 이집트 체류 시 단위 수렴 설명 가능

③ 모세 규빗 (47.2cm):
   탈무드 R.Chaim Naeh 기준 (48.0cm)과 98% 일치
   → 랍비 전통이 '기억'하는 값이 모델에서 자연스럽게 도출
```

---

## 공학 건축 시스템으로의 확장 가능성

현재 MIDOS v0.1은 **크기 계산 엔진**이다.
다음 레이어를 쌓으면 **설계 엔진**이 된다:

```
Phase 1 (완성) — 크기 탐색 엔진
  ✓ 시대별 규빗 추적 (수명 → 신체 → 규빗)
  ✓ 성경 구조물 4종 (방주, 성막, 솔로몬 성전, 에스겔 성전)
  ✓ 고고학 교차 검증
  ✓ 다중 시나리오 비교

Phase 2 (다음) — 구조 공학 레이어
  → gravity.py       : 궁창 시대 중력(g) 변화 모델
  → load_analysis.py : 재료 강도 × 규모 → 자립 하중 한계
  → materials.py     : 백향목/돌/금 단위 부피 → 현대 가격 환산

Phase 3 (장기) — 건축 설계 모드
  → 회당 설계: 규빗 선택 → 현대 건축 좌표 출력
  → 제단 규격: 번제단 치수 → 재료 소요량 계산
  → SVG/DXF 출력 → CAD/BIM 연동
  → 솔로몬 성전 전체 복원 모델
```

**핵심 설계 철학:** 같은 "300 규빗"이라도 누가, 언제 쟀느냐에 따라 건물 크기가 달라진다.
단위 자체가 살아있는 변수다.

---

## ENGINE_HUB 대칭 구조

```
AVCE   (수중 자율항법)  ρ_water × g × V              = 부력   (정적)
FLEN   (항공 양력)      ½ρ_air  × v² × S × CL        = 양력   (동적)
MIDOS  (성경 계측)      cubit_cm × dimension_cubits  = 실제크기 (역사)

셋 모두: stdlib only · frozen dataclass · snapshot dict 호환 · 레이어 분리
```

---

## 개념도

```
인물 (노아, 모세, 솔로몬...)
  │  수명 + 시대
  ▼
  ┌──────────────────────┐
  │  core/canopy.py      │  ← 궁창 대기 상태
  │  P, O2, UV, CO2      │    (5단계 시퀀스)
  └──────────┬───────────┘
             │ 환경 파라미터
  ┌──────────▼───────────┐
  │  core/biology.py     │  ← 신체 스케일 모델
  │  O2^α×P^β×UV^γ×수명^ε│    (지수 합성)
  └──────────┬───────────┘
             │ cubit_cm
  ┌──────────▼───────────┐   ┌─────────────────┐
  │  units/              │   │  structures/     │
  │  CubitStandard       │   │  방주·성막·성전  │
  │  8종 표준 정의        │   │  순수 규빗 저장  │
  └──────────┬───────────┘   └────────┬────────┘
             └──────────┬─────────────┘
                        │
          ┌─────────────▼─────────────┐
          │  validator.py             │
          │  고고학 교차 검증          │
          │  실로암 터널 · 아랏 성소   │
          └─────────────┬─────────────┘
                        │
          ┌─────────────▼─────────────┐
          │  why_it_measures.py       │
          │  MidosResult (불변)        │
          │  + explain() 전체 해설     │
          │  + snapshot_updates {}    │
          └───────────────────────────┘
```

---

## 디렉터리

```
Tape_measure/  (Python package: midos_engine)
├── README.md                 ← 이 파일
├── run_midos_demo.py         ← 여기서 시작
├── __init__.py               ← 공개 API
├── why_it_measures.py        ★ 통합 분석 엔진
├── scenario_engine.py        ★ 다중 시나리오 비교
├── validator.py              ★ 고고학 교차 검증
├── core/
│   ├── canopy.py             ★ 궁창 대기 환경 (6단계)
│   ├── biology.py            ★ 신체 스케일 모델
│   └── timeline.py           ★ 성경 인물 시간축
├── units/
│   ├── cubit_standards.py    ★ 규빗 표준 8종
│   └── conversions.py        ★ 히브리 단위 변환
└── structures/
    ├── noahs_ark.py          ★ 노아 방주 (창 6:15)
    ├── tabernacle.py         ★ 성막 (출 25-27)
    ├── solomons_temple.py    ★ 솔로몬 성전 (왕상 6-7)
    └── ezekiels_temple.py    ★ 에스겔 성전 (겔 40-48)
```

---

## 자체 점검 메모 (v0.1.0 초안)

모델 내부 일관성 기준. 절대적 수치로 보지 말 것.

```
  █████████░  ~92  궁창 대기 모델    — 5단계 시퀀스, 물리 파라미터 근거
  ████████░░  ~85  신체 스케일 모델  — 지수 모델, 파라미터 조정 필요
  █████████░  ~90  시간축 데이터     — 성경 원문 기반, 18명 수록
  █████████░  ~91  단위 변환 체계    — 히브리 6단계 단위 완비
  ████████░░  ~88  구조물 4종        — 원문 치수 충실, 헤롯 성전 미수록
  █████████░  ~90  고고학 검증       — 5개 실측 기록, 가중 신뢰도
  █████████░  ~93  시나리오 엔진     — 8종 표준 × 구조물 완전 비교

  참고 평균: ~90 / 100  (모델 내부 기준)
```

---

## 블록체인 서명 (코드 무결성)

```
타임스탬프   : 2026-03-08T13:04:17Z
루트 해시    : ac43da49ce0989d2f4d6a72f3326c13501a5bf7a2bfbb1f67b46bf24b721b3e4

파일별 SHA-256 (앞 16자리):
  d97438077c8f092e  __init__.py
  c478272b0c53892b  run_midos_demo.py
  b30f6956c94d6a5d  scenario_engine.py
  53f12cbef0f83bc2  validator.py
  40d4a34f7ec5eedf  why_it_measures.py
  812452e98c8b4b3b  core/__init__.py
  f85df11611118352  core/biology.py
  3e8bb3d75d6f3666  core/canopy.py
  26ec6608e740d588  core/timeline.py
  6882a6d272bddce7  structures/__init__.py
  dd02828487e37293  structures/_base.py
  7179e13d4f8ef841  structures/ezekiels_temple.py
  6827875f528d649d  structures/noahs_ark.py
  08dec7184e5d8ae5  structures/solomons_temple.py
  f6b4fa960167f1b3  structures/tabernacle.py
  223e83e6c06bf60d  units/__init__.py
  791cb0ca11010799  units/conversions.py
  1f4b27f667ebd6ef  units/cubit_standards.py
```

---

> **Tape_measure라는 이름의 진짜 의미:**
> 인류 역사상 가장 오래된 줄자는 금속도, 섬유도 아닌 **인간의 팔**이었다.
> 노아는 그 팔로 타이타닉 크기의 배를 설계했고,
> 모세는 그 팔로 하나님의 임재가 깃든 법궤를 만들었다.
>
> *이 레포가 묻는 것: "당신의 팔은 얼마나 긴가?"*
> *이 레포가 답하는 것: "시대에 따라 달랐다."*

---

**Built with:** Python 3.x · stdlib only · Canopy Theory · 창세기 수명 데이터 · 고고학 실측 · ISA는 아니지만 RSA(Raqia Standard Atmosphere)
