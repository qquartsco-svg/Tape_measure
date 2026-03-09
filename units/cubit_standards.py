"""
cubit_standards.py — 규빗(Cubit) 표준 정의

학파별 규빗 값 + 시대별 동적 규빗 (body scale 기반).

학술 출처:
  - Scott, R.B.Y. (1959). Biblical Archaeologist 22(2): 22-40
  - Kaufman, A.S. (1988). Palestine Exploration Quarterly 120: 74-79
  - Powell, M.A. (1992). Anchor Bible Dictionary 6: 897-908
  - Dillow, J.C. (1981). The Waters Above

히브리어 단위 계층:
  1 아마(amah)  = 2 제레트(zeret)
               = 6 테파흐(tefach)
               = 24 에츠바(etzba)
  6 아마         = 1 카네(qaneh, 갈대)
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class CubitStandard:
    """규빗 표준 (불변)"""
    name:       str    # 표준 이름
    name_kr:    str    # 한국어
    cm:         float  # 규빗 길이 (cm)
    source:     str    # 근거 문헌/유물
    period:     str    # 해당 시대
    confidence: float  # 신뢰도 0~1 (고고학 증거 강도)
    context:    str    # 적합 사용 맥락
    notes:      str = ""

    @property
    def m(self) -> float:
        return self.cm / 100.0

    @property
    def inches(self) -> float:
        return self.cm / 2.54

    def label(self) -> str:
        return f"{self.name_kr} ({self.cm:.1f}cm)"


@dataclass(frozen=True)
class UnitSystem:
    """히브리 길이 단위 체계 (규빗 기준)"""
    cubit: CubitStandard

    @property
    def etzba_cm(self) -> float:     return self.cubit.cm / 24.0
    @property
    def tefach_cm(self) -> float:    return self.cubit.cm / 6.0
    @property
    def zeret_cm(self) -> float:     return self.cubit.cm / 2.0
    @property
    def amah_cm(self) -> float:      return self.cubit.cm
    @property
    def qaneh_cm(self) -> float:     return self.cubit.cm * 6.0

    def table(self) -> str:
        return (
            f"단위 체계 [{self.cubit.name_kr}, {self.cubit.cm:.2f}cm 기준]\n"
            f"  에츠바(손가락) : {self.etzba_cm:.3f} cm\n"
            f"  테파흐(손바닥) : {self.tefach_cm:.3f} cm\n"
            f"  제레트(뼘)     : {self.zeret_cm:.3f} cm\n"
            f"  아마(규빗)     : {self.amah_cm:.3f} cm  ← 기준\n"
            f"  카네(갈대,6규빗): {self.qaneh_cm:.3f} cm\n"
        )


# ══════════════════════════════════════════════════════════════
# 표준 규빗 정의
# ══════════════════════════════════════════════════════════════

# ── 원형 논리 주의 (Circular Reasoning Warning) ─────────────────────
# CUBIT_HYPER의 89.5cm 값은 이 엔진(MIDOS)의 biology.py 모델이 출력한 값임.
# 즉, "canopy mode 가정 → 신체 스케일 → 89cm 도출" 한 것을 다시 표준으로 등록한 것.
#
# 이 값은 독립적인 고고학 증거가 없으며, 모델 내부에서만 순환적으로 확인됨.
# confidence=0.30으로 낮게 설정한 것이 이 사실을 반영함.
# validator.py의 교차 검증에서 이 표준이 "잘 맞는다"고 나오더라도
# 그것은 모델이 자신의 출력값을 검증하는 것이므로 독립적 검증이 아님.
#
# 사용 시 이 한계를 인지할 것.
CUBIT_HYPER = CubitStandard(
    name       = "Hyper Cubit",
    name_kr    = "하이퍼 규빗 (궁창 시대)",
    cm         = 89.5,
    source     = "MIDOS biology.py 모델 출력값 — 독립 고고학 증거 없음 (원형 논리)",
    period     = "Pre-Flood (아담~노아)",
    confidence = 0.30,   # 직접 고고학 증거 없음. 모델 자체 추론값.
    context    = "노아 방주 시뮬레이션, 궁창 시대 가상 설계 시나리오",
    notes      = (
        "⚠ 이 값은 MIDOS canopy mode 모델의 출력값을 표준으로 등록한 것. "
        "독립 고고학 증거 없음. validator.py 점수가 높게 나와도 "
        "원형 논리(circular reasoning)이므로 독립적 검증이 아님."
    ),
)

# 일반 히브리 규빗 (고고학 주류)
CUBIT_COMMON = CubitStandard(
    name       = "Common Hebrew Cubit",
    name_kr    = "일반 히브리 규빗",
    cm         = 44.5,
    source     = "실로암 터널 비문 (BC 701년, '1200 규빗' → 533m÷1200)",
    period     = "Iron Age II (BC 900-600)",
    confidence = 0.85,
    context    = "성막, 솔로몬 성전, 헤롯 성전 (일반 맥락)",
    notes      = "Scott(1959), Kaufman(1988). 팔레스타인 고고학 발굴 종합.",
)

# 성전/에스겔 장규빗
CUBIT_SACRED = CubitStandard(
    name       = "Sacred / Ezekiel Long Cubit",
    name_kr    = "성전 규빗 (장규빗)",
    cm         = 51.8,
    source     = "에스겔 40:5 '일반 규빗+한 손바닥' 명시. 일반규빗+tefach(7.4cm)",
    period     = "Neo-Babylonian (BC 600-500)",
    confidence = 0.90,
    context    = "에스겔 성전 (장규빗 명시), 성전 측량 맥락",
    notes      = "유일하게 성경 본문에서 규빗 값을 명시적으로 정의한 구절.",
)

# 이집트 왕실 규빗
CUBIT_EGYPTIAN = CubitStandard(
    name       = "Egyptian Royal Cubit",
    name_kr    = "이집트 왕실 규빗",
    cm         = 52.5,
    source     = "투린 박물관 마야(Maya) 측정봉 실물, 카르나크 신전 측정봉",
    period     = "New Kingdom Egypt (BC 1550-1070)",
    confidence = 0.95,
    context    = "성막 (모세 이집트 체류), 족장 시대, 이집트 영향권",
    notes      = "7 팔마 규빗. 실물 유물 10여 점 현존. 가장 신뢰도 높은 실물 증거.",
)

# 탈무드 단 규빗 (R. Chaim Naeh, 현대 정통파 표준)
CUBIT_TALMUD_S = CubitStandard(
    name       = "Talmudic Short (Naeh)",
    name_kr    = "탈무드 규빗 (R. Naeh)",
    cm         = 48.0,
    source     = "R. Chaim Naeh (20세기). 탈무드 Eruvin 3b 기반 재계산.",
    period     = "Rabbinic (현대 정통파)",
    confidence = 0.60,
    context    = "현대 할라카 (안식일 영역, 수카, 미크베)",
    notes      = "이스라엘 예루살렘 정통파 공동체 표준. 6 tefach = 1 amah 기반.",
)

# 탈무드 장 규빗 (Chazon Ish, 엄격파)
CUBIT_TALMUD_L = CubitStandard(
    name       = "Talmudic Long (Chazon Ish)",
    name_kr    = "탈무드 규빗 (Chazon Ish)",
    cm         = 57.6,
    source     = "Chazon Ish (R. Avraham Karelitz, 20세기). R. Tam 전통 지지.",
    period     = "Rabbinic (엄격파)",
    confidence = 0.55,
    context    = "베나이 브락(Bnei Brak) 정통파 공동체. 할라카 최엄격 기준.",
    notes      = "현대 정통파 중 가장 큰 규빗 값. 성전 치수 계산에 일부 사용.",
)

# 바빌로니아 규빗
CUBIT_BABYLONIAN = CubitStandard(
    name       = "Babylonian Royal Cubit",
    name_kr    = "바빌로니아 규빗",
    cm         = 49.5,
    source     = "니네베 측정봉, 네부카드네자르 시대 기록",
    period     = "Neo-Assyrian / Neo-Babylonian (BC 900-500)",
    confidence = 0.75,
    context    = "에스겔 (바빌론 포로기), 다니엘 시대",
    notes      = "에스겔이 바빌론에서 본 성전 환상 — 바빌로니아 단위 참조 가능성.",
)

# 고고학 주류 합의 (Avi-Yonah / Mazar)
CUBIT_MODERN_ARCH = CubitStandard(
    name       = "Archaeological Consensus",
    name_kr    = "고고학 합의 규빗",
    cm         = 46.0,
    source     = "Avi-Yonah(1966), Benjamin Mazar(1968-78) 헤롯 성전 발굴",
    period     = "Herodian (BC 20 ~ AD 70)",
    confidence = 0.75,
    context    = "헤롯 성전 발굴 맥락",
    notes      = "헤롯 성전 석재 블록 실측 기반. 44.5cm와 52.5cm 사이.",
)

ALL_STANDARDS: tuple[CubitStandard, ...] = (
    CUBIT_HYPER,
    CUBIT_COMMON,
    CUBIT_SACRED,
    CUBIT_EGYPTIAN,
    CUBIT_TALMUD_S,
    CUBIT_TALMUD_L,
    CUBIT_BABYLONIAN,
    CUBIT_MODERN_ARCH,
)


def cubit_from_body(cubit_cm: float, confidence: float = 0.50) -> CubitStandard:
    """생물 스케일 모델로 추정된 규빗 값으로 CubitStandard 동적 생성"""
    return CubitStandard(
        name       = f"Temporal Cubit ({cubit_cm:.1f}cm)",
        name_kr    = f"시대별 추정 규빗 ({cubit_cm:.1f}cm)",
        cm         = cubit_cm,
        source     = "MIDOS 생물 스케일 모델 (환경×수명 역산)",
        period     = "시대별 동적 계산",
        confidence = confidence,
        context    = "시대별 구조물 규모 추정",
        notes      = "직접 고고학 증거 없음. 대기 환경 + 수명 데이터 기반 추론.",
    )
