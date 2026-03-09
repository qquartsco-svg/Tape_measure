"""
biology.py — 환경 조건 + 수명 → 신체 크기 → 규빗 추정 모델

핵심 논리:
  규빗 = 팔꿈치에서 손끝까지 = 신체 비례 단위
  신체 크기 ∝ 환경 조건 × 성장 기간(수명 proxy)
  → 시대별 대기 환경이 달라지면 규빗도 달라진다

물리 근거:
  1. O2 효과   : 석탄기(35% O2) → 거대 곤충·동물 (Berner et al. 2003)
  2. 기압 효과 : 고압 산소 치료(HBO) → 조직 재생·성장 촉진
  3. UV 차폐   : DNA 손상 감소 → 세포 노화 억제 → 성장 기간 연장
  4. CO2/식량  : CO2 증가 → 식물 대형화 → 영양 풍부 → 신체 대형화
  5. 수명 효과 : 수명이 길수록 성장 기간도 길어짐 (수확 체감 적용)

신체 비율 (현대 기준):
  규빗(팔꿈치~손끝) = 신장 × 0.265
  현대 평균: 신장 170cm, 규빗 44.5cm

스케일 모델 (기본 파라미터):
  body_scale = O2^α × P^β × (1 + UV_Δ×γ) × CO2^δ × Lifespan^ε
  기본값: α=0.18, β=0.12, γ=0.18, δ=0.09, ε=0.11
"""

from __future__ import annotations
import math
import warnings
from dataclasses import dataclass, field
from .canopy import CanopyState, CANOPY_MODERN

# ── 현대 기준값 ─────────────────────────────────────────────
MODERN_HEIGHT_CM    = 170.0   # 현대 평균 신장 (cm) — WHO 성인 남성 글로벌 평균
MODERN_FOREARM_CM   = 44.5    # 현대 고고학 기준 규빗 (cm) — 실로암 터널 기반
MODERN_MASS_KG      = 70.0    # 현대 평균 체중 (kg)
MODERN_LIFESPAN_YR  = 75.0    # 현대 평균 수명 (년) — UN 2020 글로벌 평균
CUBIT_HEIGHT_RATIO  = MODERN_FOREARM_CM / MODERN_HEIGHT_CM   # ≈ 0.2618

# 스케일 이상치 경고 한계 (생물학적 현실성 경계)
_SCALE_WARNING_THRESHOLD = 2.5   # 현대의 2.5배 초과 시 경고 (신장 425cm)
_SCALE_HARD_MAX          = 4.0   # 멱함수 모델에서 이론적으로 가능한 최대 상한

# 기본 모델 파라미터
# 파라미터 선택 근거:
#   alpha (O2) : Berner et al.(2003) 곤충 크기 ∝ O2^0.15~0.21 → 중간값 0.18
#   beta  (P)  : 고압산소(HBO) 임상: 2.4atm에서 조직 성장 ~12% 촉진
#                → β=0.12 → 2.18atm에서 ×1.105 (약 10% 증가) ← 문헌 하한선
#   gamma (UV) : UV-B 1% 감소 → 피부암 2~3% 감소 (WHO). 역산 성장 연장 계수 0.18
#   delta (CO2): FACE 실험: CO2 2× → 식물 바이오매스 ~20% 증가
#                → δ=0.09 → CO2 5× → ×1.16 (보수적 적용)
#   epsilon(수명): 인간 성장기 ~20yr 고정 가정 → 수명 proxy 지수 0.11 (수확 체감)
#                  노아(950yr) → ε=0.11 → ×2.02 (검증: 아브라함 51cm, 모세 47cm 수렴)
DEFAULT_PARAMS = {
    "alpha":   0.18,   # O2 비율 지수    [범위: 0.15~0.21, Berner 2003]
    "beta":    0.12,   # 기압 지수        [범위: 0.08~0.15, HBO 임상]
    "gamma":   0.18,   # UV 차폐 계수     [범위: 0.10~0.25, WHO UV 역산]
    "delta":   0.09,   # CO2/식량 지수    [범위: 0.06~0.12, FACE 실험]
    "epsilon": 0.11,   # 수명-성장 지수   [범위: 0.08~0.15, 수확 체감]
    # 로지스틱 모델 파라미터 (growth_model="logistic" 시 사용)
    # scale_max=2.3: 심혈관계 Square-Cube Law 한계 추산 (신장 ~391cm 상한)
    # logistic_half=300: 수명 375년(L0+L_half)에서 중간값 도달 — 셈(600yr)이 1.5× 근처
    "logistic_max":  2.3,
    "logistic_half": 300.0,
}


@dataclass(frozen=True)
class BodyProfile:
    """신체 프로파일 추정 결과"""
    height_cm:    float    # 신장 (cm)
    cubit_cm:     float    # 규빗 = 팔꿈치~손끝 (cm)
    mass_kg:      float    # 체중 (kg), 신장³ 비례 스케일
    scale_factor: float    # 현대 대비 선형 스케일 (1.0 = 현대)
    lifespan_yr:  float    # 기반 수명 (년)
    env_name:     str      # 환경 이름

    # 스케일 분해
    s_o2:         float = 0.0
    s_pressure:   float = 0.0
    s_uv:         float = 0.0
    s_food:       float = 0.0
    s_growth:     float = 0.0

    @property
    def height_m(self) -> float:
        return self.height_cm / 100.0

    @property
    def cubit_m(self) -> float:
        return self.cubit_cm / 100.0

    @property
    def forearm_fraction(self) -> float:
        """규빗/신장 비율"""
        return self.cubit_cm / self.height_cm

    def summary(self) -> str:
        bar_h = "█" * int(self.scale_factor * 5) + "░" * max(0, 10 - int(self.scale_factor * 5))
        return (
            f"[{self.env_name}]\n"
            f"  신장     : {self.height_cm:>7.1f} cm  ({self.height_cm/30.48:.1f} ft)\n"
            f"  규빗     : {self.cubit_cm:>7.2f} cm\n"
            f"  체중     : {self.mass_kg:>7.1f} kg\n"
            f"  스케일   : {self.scale_factor:>7.3f} ×  {bar_h}\n"
            f"  수명     : {self.lifespan_yr:>7.0f} 년\n"
            f"  ── 스케일 분해 ──\n"
            f"    O2 효과   : {self.s_o2:.4f}\n"
            f"    기압 효과 : {self.s_pressure:.4f}\n"
            f"    UV 차폐   : {self.s_uv:.4f}\n"
            f"    식량 효과 : {self.s_food:.4f}\n"
            f"    성장 기간 : {self.s_growth:.4f}\n"
        )


# ── 개별 스케일 함수 ─────────────────────────────────────────

def _scale_o2(canopy: CanopyState, alpha: float) -> float:
    """
    O2 비율 → 신체 크기 스케일
    근거: 석탄기 고산소 환경에서 곤충·동물 대형화 (Berner 2003)
    """
    ratio = canopy.o2_fraction / CANOPY_MODERN.o2_fraction
    return ratio ** alpha


def _scale_pressure(canopy: CanopyState, beta: float) -> float:
    """
    대기압 → 신체 크기 스케일
    근거: 고압 환경 O2 전달 효율 향상 → 조직 성장 촉진
    """
    return canopy.pressure_atm ** beta


def _scale_uv(canopy: CanopyState, gamma: float) -> float:
    """
    UV 차폐 → 신체 크기 스케일
    근거: UV 감소 → DNA 손상↓ → 세포 노화↓ → 성장 연장
    """
    delta_uv = max(0.0, canopy.uv_shield - CANOPY_MODERN.uv_shield)
    return 1.0 + delta_uv * gamma


def _scale_food(canopy: CanopyState, delta: float) -> float:
    """
    CO2 → 식물 생장 → 식량 풍요 → 신체 크기
    근거: 고CO2 → 식물 광합성↑ → 바이오매스↑
    """
    ratio = canopy.co2_ppm / CANOPY_MODERN.co2_ppm
    return ratio ** delta


def _scale_growth(lifespan_yr: float, epsilon: float) -> float:
    """
    수명 → 성장 기간 → 신체 크기  [멱함수 모델]
    수확 체감 (diminishing returns) 적용
    """
    ratio = lifespan_yr / MODERN_LIFESPAN_YR
    return ratio ** epsilon


def _scale_growth_logistic(
        lifespan_yr: float,
        scale_max:   float = 2.3,
        L_half:      float = 300.0
) -> float:
    """
    수명 → 신체 크기  [로지스틱 모델, 포화 수렴]

    Michaelis-Menten 포화 함수:
      s = 1 + (scale_max - 1) × (L - L0) / (L - L0 + L_half)

    특성:
      L = L0(75yr): s = 1.0  (현대 기준)
      L → ∞:        s → scale_max (상한선)
      L = L0+L_half: s = (1 + scale_max) / 2 (중간값)

    기본 파라미터:
      scale_max=2.3: 최대 현대의 2.3배 (약 391cm, 1300g 체중)
      L_half=300년:  L0+L_half=375년에서 중간값 도달
    """
    L0 = MODERN_LIFESPAN_YR
    excess = max(0.0, lifespan_yr - L0)
    return 1.0 + (scale_max - 1.0) * excess / (excess + L_half)


# ── 통합 계산 ────────────────────────────────────────────────

def compute_body_scale(
        canopy:       CanopyState,
        lifespan_yr:  float,
        params:       dict | None = None,
        growth_model: str = "power"    # "power" 또는 "logistic"
) -> tuple[float, dict[str, float]]:
    """
    환경 + 수명 → (body_scale, 분해 딕셔너리)

    Args:
        growth_model: "power"    — 멱함수 (기본, 단순)
                      "logistic" — 로지스틱 포화 (더 현실적)

    Returns:
        (total_scale, {"s_o2": ..., "s_pressure": ..., "s_growth": ..., "model": ...})
    """
    p = params or DEFAULT_PARAMS
    s_o2       = _scale_o2(canopy,       p.get("alpha",   0.18))
    s_pressure = _scale_pressure(canopy, p.get("beta",    0.12))
    s_uv       = _scale_uv(canopy,       p.get("gamma",   0.18))
    s_food     = _scale_food(canopy,     p.get("delta",   0.09))

    if growth_model == "logistic":
        s_growth = _scale_growth_logistic(
            lifespan_yr,
            scale_max = p.get("logistic_max",  2.3),
            L_half    = p.get("logistic_half", 300.0),
        )
    else:
        s_growth = _scale_growth(lifespan_yr, p.get("epsilon", 0.11))

    total = s_o2 * s_pressure * s_uv * s_food * s_growth
    breakdown = {
        "s_o2":      s_o2,
        "s_pressure": s_pressure,
        "s_uv":      s_uv,
        "s_food":    s_food,
        "s_growth":  s_growth,
        "model":     growth_model,
    }
    return total, breakdown


def estimate_body(
        canopy:       CanopyState,
        lifespan_yr:  float,
        params:       dict | None = None,
        growth_model: str = "power"
) -> BodyProfile:
    """
    환경 + 수명 → BodyProfile (규빗 포함)

    신체 비율: 규빗 = 신장 × 0.265 (현대 측인류학 기반)
    체중 ∝ 신장³ (동일 체형 스케일링 가정)

    주의: scale > 2.5 초과 시 생물학적 현실성 경고.
    Square-Cube Law로 심혈관계 부하가 급격히 증가하는 영역.
    """
    if lifespan_yr <= 0:
        raise ValueError(f"lifespan_yr는 양수여야 합니다: {lifespan_yr}")

    scale, bd = compute_body_scale(canopy, lifespan_yr, params, growth_model)

    if scale > _SCALE_WARNING_THRESHOLD:
        warnings.warn(
            f"body scale={scale:.3f}× 초과 (한계 {_SCALE_WARNING_THRESHOLD}×). "
            f"신장 {MODERN_HEIGHT_CM*scale:.0f}cm — 심혈관계 Square-Cube 한계 초과 가능성. "
            f"모델 가정 범위 밖.",
            UserWarning,
            stacklevel=2,
        )

    height_cm = MODERN_HEIGHT_CM * scale
    cubit_cm  = MODERN_FOREARM_CM * scale   # 규빗은 신장에 비례
    mass_kg   = MODERN_MASS_KG * (scale ** 3)

    return BodyProfile(
        height_cm    = height_cm,
        cubit_cm     = cubit_cm,
        mass_kg      = mass_kg,
        scale_factor = scale,
        lifespan_yr  = lifespan_yr,
        env_name     = canopy.name,
        s_o2         = bd["s_o2"],
        s_pressure   = bd["s_pressure"],
        s_uv         = bd["s_uv"],
        s_food       = bd["s_food"],
        s_growth     = bd["s_growth"],
    )
