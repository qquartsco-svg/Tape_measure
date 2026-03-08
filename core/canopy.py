"""
canopy.py — 궁창(Raqia) 대기 환경 상태 모델

창세기 1:6-8 궁창(רָקִיעַ raqia) 이론 기반 물리 파라미터.
Canopy Theory (Dillow 1981, "The Waters Above") 참조.

핵심 가설:
  - 창조 시 지구 대기권 위에 수증기/얼음 층(궁창) 존재
  - 이 층이 UV 차폐 + 온실 효과 + 대기압 증가 유발
  - 창 7:11 "하늘의 창들이 열려" = 궁창 붕괴 → 40일 폭우
  - 홍수 이후 환경 급변 → 수명 감소 → 신체 크기 감소

환경 파라미터:
  pressure_atm  : 대기압 (현재 = 1.0 atm)
  o2_fraction   : 산소 비율 (현재 = 0.21)
  co2_ppm       : CO2 농도 ppm (현재 ≈ 420)
  uv_shield     : UV 차폐율 0~1 (현재 오존층만 ≈ 0.20)
  temp_mean_C   : 연평균 기온 °C
  humidity      : 평균 습도 0~1
"""

from __future__ import annotations
from dataclasses import dataclass

_MODERN_O2   = 0.21
_MODERN_P    = 1.00
_MODERN_CO2  = 420.0
_MODERN_UV   = 0.20


@dataclass(frozen=True)
class CanopyState:
    """궁창 대기 환경 상태 (불변 스냅샷)"""
    name:          str
    pressure_atm:  float   # 대기압 (atm), 현재 = 1.0
    o2_fraction:   float   # 산소 비율 (0~1), 현재 = 0.21
    co2_ppm:       float   # CO2 농도 (ppm), 현재 ≈ 420
    uv_shield:     float   # UV 차폐율 (0~1), 현재 오존층 ≈ 0.20
    temp_mean_C:   float   # 연평균 기온 (°C)
    humidity:      float   # 평균 습도 (0~1)
    description:   str = ""

    # ── 파생 속성 ────────────────────────────────────────────

    @property
    def o2_relative(self) -> float:
        """현재 대비 산소 비율"""
        return self.o2_fraction / _MODERN_O2

    @property
    def pressure_relative(self) -> float:
        """현재 대비 대기압 비율"""
        return self.pressure_atm / _MODERN_P

    @property
    def co2_relative(self) -> float:
        """현재 대비 CO2 비율"""
        return self.co2_ppm / _MODERN_CO2

    @property
    def effective_o2_pp_atm(self) -> float:
        """유효 산소 분압 (atm) = pressure × o2_fraction"""
        return self.pressure_atm * self.o2_fraction

    @property
    def uv_shield_delta(self) -> float:
        """현재 대비 추가 UV 차폐량 (음수 불가)"""
        return max(0.0, self.uv_shield - _MODERN_UV)

    def info(self) -> str:
        return (
            f"[{self.name}]\n"
            f"  대기압   : {self.pressure_atm:.2f} atm ({self.pressure_relative:.2f}×)\n"
            f"  산소     : {self.o2_fraction*100:.1f}% ({self.o2_relative:.2f}×)\n"
            f"  CO2      : {self.co2_ppm:.0f} ppm ({self.co2_relative:.2f}×)\n"
            f"  UV 차폐  : {self.uv_shield*100:.0f}%\n"
            f"  기온     : {self.temp_mean_C:.1f}°C\n"
            f"  습도     : {self.humidity*100:.0f}%\n"
            f"  설명     : {self.description}\n"
        )


# ═══════════════════════════════════════════════════════════════
# 사전 정의 대기 상태
# ═══════════════════════════════════════════════════════════════

# 궁창 시대 (아담~노아, 창 1~7장)
CANOPY_PRE_FLOOD = CanopyState(
    name         = "Pre-Flood | 궁창 시대",
    pressure_atm = 2.18,    # ~2배 가압 (Dillow 1981 추정)
    o2_fraction  = 0.30,    # 30% O2 (석탄기 유사 — 거대 생물 지지)
    co2_ppm      = 2000.0,  # 현재의 ~5배 (온실 효과, 식생 폭발)
    uv_shield    = 0.95,    # 95% UV 차폐 (수증기층)
    temp_mean_C  = 27.0,    # 균일 온난 (계절 없음, 창 2:5~6 이슬)
    humidity     = 0.92,    # 고습도
    description  = (
        "창세기 1-7장. 궁창(수증기층) 완전 유지. 높은 산소·기압·UV 차폐. "
        "석탄기(Carboniferous) 유사 환경. 거대 생물 서식 가능. "
        "아담~노아 세대, 수명 900년대."
    ),
)

# 홍수 직후 과도기 (창 8~11장, 셈~에벨 시대)
CANOPY_EARLY_POST = CanopyState(
    name         = "Early Post-Flood | 홍수 직후",
    pressure_atm = 1.40,
    o2_fraction  = 0.24,
    co2_ppm      = 800.0,
    uv_shield    = 0.45,
    temp_mean_C  = 18.0,
    humidity     = 0.72,
    description  = (
        "창세기 8-11장. 궁창 붕괴 직후 과도기. 빙하기 가능성. "
        "환경 급변 시기. 셈~에벨 시대, 수명 400-600년대."
    ),
)

# 족장 시대 (창 12~50장, 아브라함~요셉, BC 2100-1600)
CANOPY_PATRIARCHAL = CanopyState(
    name         = "Patriarchal | 족장 시대",
    pressure_atm = 1.10,
    o2_fraction  = 0.22,
    co2_ppm      = 500.0,
    uv_shield    = 0.25,
    temp_mean_C  = 16.0,
    humidity     = 0.63,
    description  = (
        "창세기 12-50장. 아브라함~요셉. 환경이 현재에 근접. "
        "수명 110-175년대. 이집트 왕실 규빗 시대와 겹침."
    ),
)

# 모세·성막 시대 (출애굽 BC 1446, 수명 120년대)
CANOPY_MOSAIC = CanopyState(
    name         = "Mosaic | 모세·성막 시대",
    pressure_atm = 1.02,
    o2_fraction  = 0.21,
    co2_ppm      = 430.0,
    uv_shield    = 0.21,
    temp_mean_C  = 15.5,
    humidity     = 0.61,
    description  = (
        "출애굽기~신명기. 성막 건설 시대. 환경이 현재와 거의 동일. "
        "수명 120년대. 이집트 규빗 영향권."
    ),
)

# 왕국 시대 (다윗~솔로몬, BC 1000-900)
CANOPY_KINGDOM = CanopyState(
    name         = "Kingdom | 왕국 시대",
    pressure_atm = 1.01,
    o2_fraction  = 0.21,
    co2_ppm      = 425.0,
    uv_shield    = 0.20,
    temp_mean_C  = 15.2,
    humidity     = 0.60,
    description  = (
        "열왕기상하. 다윗~솔로몬·에스겔. 성전 건설 시대. "
        "환경 현재와 동일. 수명 60-70년대."
    ),
)

# 현재 기준 (기준값)
CANOPY_MODERN = CanopyState(
    name         = "Modern | 현대",
    pressure_atm = 1.00,
    o2_fraction  = 0.21,
    co2_ppm      = 420.0,
    uv_shield    = 0.20,
    temp_mean_C  = 15.0,
    humidity     = 0.60,
    description  = "현재 대기 환경. 모든 비율의 기준값 (1.0).",
)

# 시간순 시퀀스
ERA_SEQUENCE: tuple[CanopyState, ...] = (
    CANOPY_PRE_FLOOD,
    CANOPY_EARLY_POST,
    CANOPY_PATRIARCHAL,
    CANOPY_MOSAIC,
    CANOPY_KINGDOM,
    CANOPY_MODERN,
)
