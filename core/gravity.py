"""
gravity.py — 궁창 시대 중력 및 대기 구조 하중 모델

"노아가 270m짜리 배를 지을 수 있었던 물리적 조건은?"

핵심 주제:
  중력(g) 자체는 거의 변하지 않지만,
  대기 환경(압력, 밀도)이 달라지면 구조물이 받는
  바람 하중 · 부력 · 유효 하중이 크게 달라진다.

물리 분석:
  1. 중력 자체 (보수적):
     g ≈ 9.81 m/s²  → 창조과학 일부: 자전 증가 → g_eff 미세 감소
     채택: 시나리오별 설정 가능, 기본은 현재 동일

  2. 대기 밀도 변화 (가장 중요):
     2.18atm × 1.29 kg/m³ = 2.81 kg/m³  (현재 1.22 kg/m³)
     → 바람 하중 ∝ ρ_air × v²  → 2.3배
     → 큰 구조물에 치명적 영향

  3. 재료별 부력 보정 (미미):
     석재(2400 kg/m³): 부력 +0.12% → 무시
     목재(600 kg/m³) : 부력 +0.47% → 무시

  4. 자전 속도 가설 (극단적 시나리오):
     12시간 하루 → ω = 2×2π/86400 → g_eff 감소 ~0.3%
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from .canopy import CanopyState, CANOPY_PRE_FLOOD, CANOPY_MODERN

_G0     = 9.80665   # 표준 중력 가속도 (m/s²)
_R_EARTH = 6.371e6   # 지구 반경 (m)
_M_AIR  = 0.02897   # 공기 몰 질량 (kg/mol)
_R_GAS  = 8.314     # 기체 상수 (J/mol·K)


@dataclass(frozen=True)
class GravityState:
    """중력 + 대기 환경 상태 (구조 하중 계산용)"""
    name:          str
    g_ms2:         float    # 중력 가속도 (m/s²)
    air_density:   float    # 대기 밀도 (kg/m³)
    wind_factor:   float    # 바람 하중 배율 (현재 = 1.0)
    description:   str = ""

    @property
    def g_relative(self) -> float:
        """현재 대비 중력 비율"""
        return self.g_ms2 / _G0

    @property
    def wind_pressure_factor(self) -> float:
        """바람 동압 배율 (ρ × v² 기준, v 동일 가정)"""
        return self.air_density / 1.225

    def info(self) -> str:
        return (
            f"[{self.name}]\n"
            f"  중력 가속도   : {self.g_ms2:.4f} m/s²  ({self.g_relative:.4f}×)\n"
            f"  대기 밀도     : {self.air_density:.3f} kg/m³\n"
            f"  바람 하중 배율: {self.wind_pressure_factor:.3f}×\n"
            f"  설명: {self.description}\n"
        )


# ── 대기 밀도 계산 ────────────────────────────────────────────

def air_density_from_canopy(canopy: CanopyState) -> float:
    """
    이상기체 법칙으로 대기 밀도 계산.
    ρ = P × M_air / (R × T)
    """
    if canopy.pressure_atm <= 0:
        raise ValueError(f"pressure_atm은 양수여야 합니다: {canopy.pressure_atm}")
    T_k = canopy.temp_mean_C + 273.15
    if T_k <= 0:
        raise ValueError(
            f"온도가 절대영도 이하입니다: {canopy.temp_mean_C}°C → {T_k}K"
        )
    P_pa = canopy.pressure_atm * 101325.0   # atm → Pa
    rho  = P_pa * _M_AIR / (_R_GAS * T_k)
    return rho


# ── 사전 정의 중력 상태 ──────────────────────────────────────

def gravity_from_canopy(
        canopy: CanopyState,
        rotation_factor: float = 1.0,   # 자전 속도 배율 (1.0 = 현재)
        g_base: float = _G0
) -> GravityState:
    """
    대기 환경으로부터 GravityState 생성.

    Args:
        canopy:           대기 환경
        rotation_factor:  자전 속도 (>1 = 빠른 자전 → g_eff 감소)
        g_base:           기본 중력 (m/s²)
    """
    rho = air_density_from_canopy(canopy)

    # 원심력 보정 (적도 기준)
    # g_eff = g - ω²R,  ω = ω0 × rotation_factor
    omega_0  = 2 * math.pi / 86400.0   # 현재 자전 각속도 (rad/s)
    omega    = omega_0 * rotation_factor
    g_centrifugal = omega ** 2 * _R_EARTH
    g_eff    = g_base - g_centrifugal + (omega_0 ** 2 * _R_EARTH)
    # ↑ 현재의 원심 보정을 이미 포함하므로 차분만 취함
    g_eff    = g_base - (omega ** 2 - omega_0 ** 2) * _R_EARTH

    wind_factor = rho / 1.225   # ISA 표준 대기 밀도 기준

    return GravityState(
        name        = canopy.name,
        g_ms2       = g_eff,
        air_density = rho,
        wind_factor = wind_factor,
        description = (
            f"P={canopy.pressure_atm:.2f}atm, "
            f"T={canopy.temp_mean_C:.0f}°C, "
            f"자전={rotation_factor:.1f}×"
        ),
    )


# ── 사전 정의 ─────────────────────────────────────────────────

# 궁창 시대 (보수적 — g 동일, 대기 밀도만 증가)
GRAVITY_PRE_FLOOD = gravity_from_canopy(CANOPY_PRE_FLOOD, rotation_factor=1.0)

# 궁창 시대 (자전 2배 가설 — 극단적 시나리오)
GRAVITY_PRE_FLOOD_FAST_SPIN = gravity_from_canopy(CANOPY_PRE_FLOOD, rotation_factor=2.0)

# 현재 기준
GRAVITY_MODERN = gravity_from_canopy(CANOPY_MODERN, rotation_factor=1.0)


# ── 구조 하중 계산 유틸리티 ──────────────────────────────────

@dataclass(frozen=True)
class AtmosphericLoad:
    """바람·대기에 의한 구조 하중 분석"""
    canopy:       CanopyState
    gravity:      GravityState
    wind_speed_ms: float   # 설계 풍속 (m/s)

    @property
    def wind_dynamic_pressure(self) -> float:
        """바람 동압 q = ½ρv²  (Pa)"""
        return 0.5 * self.gravity.air_density * self.wind_speed_ms ** 2

    @property
    def modern_wind_pressure(self) -> float:
        """현재 같은 풍속의 동압 (Pa)"""
        return 0.5 * 1.225 * self.wind_speed_ms ** 2

    @property
    def wind_pressure_ratio(self) -> float:
        """궁창 시대 / 현재 바람 동압 비율"""
        return self.wind_dynamic_pressure / self.modern_wind_pressure

    def on_wall(self, area_m2: float, Cd: float = 1.3) -> float:
        """벽면에 작용하는 바람 하중 (kN)"""
        return self.wind_dynamic_pressure * Cd * area_m2 / 1000.0

    def info(self) -> str:
        return (
            f"[대기 구조 하중 분석]\n"
            f"  설계 풍속     : {self.wind_speed_ms:.1f} m/s\n"
            f"  현재 바람 동압: {self.modern_wind_pressure:.1f} Pa\n"
            f"  시대 바람 동압: {self.wind_dynamic_pressure:.1f} Pa\n"
            f"  배율          : {self.wind_pressure_ratio:.2f}×\n"
            f"  중력 가속도   : {self.gravity.g_ms2:.4f} m/s²\n"
        )


def atmospheric_load(
        canopy: CanopyState,
        wind_speed_ms: float = 30.0,
        rotation_factor: float = 1.0
) -> AtmosphericLoad:
    """대기 상태 → 구조 하중 객체 생성"""
    g = gravity_from_canopy(canopy, rotation_factor)
    return AtmosphericLoad(
        canopy        = canopy,
        gravity       = g,
        wind_speed_ms = wind_speed_ms,
    )
