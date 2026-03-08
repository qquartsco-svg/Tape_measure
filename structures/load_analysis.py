"""
load_analysis.py — 성경 구조물 구조 하중 분석

"노아 방주가 270m라면 물 위에서 버틸 수 있었나?"
"야긴·보아스 기둥(높이 8m, 청동)이 실제로 서 있을 수 있나?"
"하이퍼 규빗 적용 솔로몬 성전의 지붕 보는 안전한가?"

재료 강도 (참고값):
  고페르나무(방주) : 압축강도 35-45 MPa, E=10 GPa
  백향목(성전)     : 압축강도 40 MPa,    E=9.5 GPa
  청동(기둥·기물) : 항복강도 200 MPa,   E=110 GPa
  석회암(토대·벽) : 압축강도 50 MPa
  화강암(토대)     : 압축강도 200 MPa

공학 공식:
  기둥 압축 응력  : σ = F/A = ρ×h×g  [MPa]
  오일러 좌굴 하중 : P_cr = π²EI/(KL)²  [N]
  보 최대 처짐    : δ_max = 5qL⁴/(384EI)  [m]
  보 최대 응력    : σ_max = M×c/I = qL²/(8Z)  [MPa]
  선박 굽힘 모멘트: M ≈ Δ×L/8 (단순화)  [kN·m]
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from ..core.gravity import GravityState, GRAVITY_PRE_FLOOD, GRAVITY_MODERN

_G0 = 9.80665


# ══════════════════════════════════════════════════════════════
# 재료 데이터베이스
# ══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Material:
    """건설 재료 물성"""
    name:          str
    name_kr:       str
    density_kgm3:  float   # 밀도 (kg/m³)
    comp_MPa:      float   # 압축 강도 (MPa)
    tens_MPa:      float   # 인장 강도 (MPa)
    E_GPa:         float   # 탄성 계수 (GPa)
    ref:           str = ""


MATERIALS: dict[str, Material] = {
    "gopher_wood": Material(
        "Gopher Wood", "고페르나무 (방주)",
        density_kgm3=600, comp_MPa=42, tens_MPa=8, E_GPa=10.0,
        ref="창 6:14. 수종 불명. 침엽수 계열 추정.",
    ),
    "cedar": Material(
        "Cedar of Lebanon", "레바논 백향목 (성전)",
        density_kgm3=560, comp_MPa=40, tens_MPa=7, E_GPa=9.5,
        ref="왕상 6:9-18. 솔로몬 성전 보·서까래·벽 내장재.",
    ),
    "bronze": Material(
        "Cast Bronze", "청동 (기둥·바다·기물)",
        density_kgm3=8800, comp_MPa=300, tens_MPa=200, E_GPa=110.0,
        ref="왕상 7:15-47. 야긴·보아스, 놋바다, 그릇들.",
    ),
    "limestone": Material(
        "Dressed Limestone", "다듬은 석회암 (벽)",
        density_kgm3=2400, comp_MPa=50, tens_MPa=5, E_GPa=20.0,
        ref="왕상 6:7. '다듬은 돌'. 솔로몬 성전 외벽.",
    ),
    "granite": Material(
        "Granite (foundation)", "화강암 (기초)",
        density_kgm3=2700, comp_MPa=200, tens_MPa=10, E_GPa=50.0,
        ref="기초 추정. 솔로몬 성전 나할 히드케온(Kidron) 계곡 기초.",
    ),
    "gold_overlay": Material(
        "Gold Overlay", "금 도금 (내부)",
        density_kgm3=19300, comp_MPa=120, tens_MPa=120, E_GPa=79.0,
        ref="왕상 6:20-22. 지성소 내부 전체 금으로 입힘.",
    ),
    "acacia": Material(
        "Acacia (Shittim)", "아카시아(싯딤) 나무 (성막)",
        density_kgm3=680, comp_MPa=45, tens_MPa=10, E_GPa=10.5,
        ref="출 25:5. 성막 기둥·법궤 재료.",
    ),
}


# ══════════════════════════════════════════════════════════════
# 단면 형상 유틸리티
# ══════════════════════════════════════════════════════════════

def circle_I(d: float) -> float:
    """원형 단면 2차 모멘트 I = πd⁴/64  (m⁴)"""
    return math.pi * d ** 4 / 64.0

def rect_I(b: float, h: float) -> float:
    """직사각형 단면 I = bh³/12  (m⁴)"""
    return b * h ** 3 / 12.0

def circle_A(d: float) -> float:
    """원형 단면 면적 A = πd²/4  (m²)"""
    return math.pi * d ** 2 / 4.0

def rect_A(b: float, h: float) -> float:
    return b * h


# ══════════════════════════════════════════════════════════════
# 결과 클래스
# ══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ColumnResult:
    """기둥 구조 분석 결과"""
    name:           str
    material:       Material
    height_m:       float
    diameter_m:     float
    gravity:        GravityState
    # 계산 결과
    mass_kg:        float
    axial_stress_MPa:  float    # 축방향 압축 응력
    euler_load_kN:     float    # 오일러 좌굴 하중
    safety_stress:     float    # 안전 계수 (강도/응력)
    safety_buckling:   float    # 좌굴 안전 계수

    @property
    def is_safe_stress(self) -> bool:
        return self.safety_stress >= 3.0

    @property
    def is_safe_buckling(self) -> bool:
        return self.safety_buckling >= 3.0

    def report(self) -> str:
        ok_s = "✓" if self.is_safe_stress   else "✗"
        ok_b = "✓" if self.is_safe_buckling else "✗"
        return (
            f"  [{self.name}] 재료: {self.material.name_kr}\n"
            f"    치수         : 높이 {self.height_m:.2f}m × 직경 {self.diameter_m:.2f}m\n"
            f"    자중         : {self.mass_kg/1000:.2f} t\n"
            f"    압축 응력    : {self.axial_stress_MPa:.3f} MPa\n"
            f"    {ok_s} 압축 안전계수: {self.safety_stress:.1f} (허용 ≥ 3.0)\n"
            f"    오일러 좌굴  : {self.euler_load_kN:.0f} kN\n"
            f"    {ok_b} 좌굴 안전계수: {self.safety_buckling:.1f} (허용 ≥ 3.0)\n"
        )


@dataclass(frozen=True)
class BeamResult:
    """보(Beam) 구조 분석 결과"""
    name:           str
    material:       Material
    span_m:         float
    width_m:        float
    depth_m:        float
    gravity:        GravityState
    load_kN_per_m:  float       # 분포 하중 (kN/m)
    # 결과
    max_deflection_mm:  float
    max_stress_MPa:     float
    allowable_defl_mm:  float   # 허용 처짐 (span/300)
    safety_factor:      float

    @property
    def is_safe_deflection(self) -> bool:
        return self.max_deflection_mm <= self.allowable_defl_mm

    @property
    def is_safe_stress(self) -> bool:
        return self.safety_factor >= 2.5

    def report(self) -> str:
        ok_d = "✓" if self.is_safe_deflection else "✗"
        ok_s = "✓" if self.is_safe_stress else "✗"
        return (
            f"  [{self.name}] 재료: {self.material.name_kr}\n"
            f"    단면         : {self.width_m*100:.0f}cm × {self.depth_m*100:.0f}cm, 스팬 {self.span_m:.2f}m\n"
            f"    분포 하중    : {self.load_kN_per_m:.2f} kN/m\n"
            f"    {ok_d} 최대 처짐   : {self.max_deflection_mm:.1f} mm  (허용 {self.allowable_defl_mm:.0f} mm = L/300)\n"
            f"    {ok_s} 최대 응력   : {self.max_stress_MPa:.2f} MPa  (안전계수 {self.safety_factor:.1f})\n"
        )


@dataclass(frozen=True)
class ArkHullResult:
    """노아 방주 선체 굽힘 분석"""
    cubit_cm:      float
    gravity:       GravityState
    length_m:      float
    width_m:       float
    height_m:      float
    # 하중
    displacement_t:   float    # 배수량 (ton)
    hogging_moment_MNm: float  # 최대 굽힘 모멘트 (MN·m)
    required_Z_m3:   float    # 필요 단면 계수 (m³)
    hull_thickness_m: float   # 추정 요구 선체 두께 (m)
    # 검증
    draft_m:         float    # 흘수 (m)
    freeboard_m:     float    # 건현 (m)

    def report(self) -> str:
        return (
            f"  [노아 방주 선체 분석] 규빗={self.cubit_cm:.1f}cm\n"
            f"    치수         : {self.length_m:.1f}m × {self.width_m:.1f}m × {self.height_m:.1f}m\n"
            f"    배수량       : {self.displacement_t:.0f} ton\n"
            f"    흘수         : {self.draft_m:.2f} m\n"
            f"    건현         : {self.freeboard_m:.2f} m\n"
            f"    최대 굽힘 모멘트: {self.hogging_moment_MNm:.1f} MN·m\n"
            f"    필요 단면 계수  : {self.required_Z_m3:.2f} m³\n"
            f"    추정 선체 두께  : {self.hull_thickness_m*100:.0f} cm\n"
        )


# ══════════════════════════════════════════════════════════════
# 분석 함수들
# ══════════════════════════════════════════════════════════════

def analyze_column(
        name:       str,
        material:   Material,
        height_m:   float,
        diameter_m: float,
        gravity:    GravityState | None = None,
        K:          float = 2.0,    # 유효 길이 계수 (K=2: 핀-자유)
) -> ColumnResult:
    """
    원형 단면 기둥 구조 분석.
    K=2.0: 하단 고정, 상단 자유 (야긴·보아스 형태)
    K=1.0: 양단 핀
    """
    g = gravity or GRAVITY_MODERN
    A = circle_A(diameter_m)
    I = circle_I(diameter_m)
    V = A * height_m

    # 자중
    mass_kg   = material.density_kgm3 * V
    weight_kN = mass_kg * g.g_ms2 / 1000.0

    # 축방향 압축 응력 (자중만)
    axial_stress_Pa  = material.density_kgm3 * height_m * g.g_ms2
    axial_stress_MPa = axial_stress_Pa / 1e6

    # 오일러 좌굴 하중
    Le = K * height_m
    euler_N   = (math.pi ** 2 * material.E_GPa * 1e9 * I) / Le ** 2
    euler_kN  = euler_N / 1000.0

    safety_stress   = material.comp_MPa / axial_stress_MPa
    safety_buckling = euler_kN / weight_kN

    return ColumnResult(
        name             = name,
        material         = material,
        height_m         = height_m,
        diameter_m       = diameter_m,
        gravity          = g,
        mass_kg          = mass_kg,
        axial_stress_MPa = axial_stress_MPa,
        euler_load_kN    = euler_kN,
        safety_stress    = safety_stress,
        safety_buckling  = safety_buckling,
    )


def analyze_beam(
        name:          str,
        material:      Material,
        span_m:        float,
        width_m:       float,
        depth_m:       float,
        floor_load_kPa: float = 2.0,    # 바닥 하중 (kPa)
        gravity:       GravityState | None = None,
) -> BeamResult:
    """
    단순 지지 직사각형 보 분석.
    균등 분포 하중 (자중 + 바닥 하중).
    """
    g = gravity or GRAVITY_MODERN
    I = rect_I(width_m, depth_m)
    A = rect_A(width_m, depth_m)

    # 분포 하중 (kN/m): 자중 + 바닥 하중
    w_self  = material.density_kgm3 * A * g.g_ms2 / 1000.0   # kN/m
    w_floor = floor_load_kPa * width_m                         # kN/m
    w_total = w_self + w_floor

    # 최대 처짐 δ = 5qL⁴/(384EI)
    q = w_total * 1000.0  # N/m
    E = material.E_GPa * 1e9  # Pa
    delta_m = 5 * q * span_m ** 4 / (384 * E * I)
    delta_mm = delta_m * 1000.0

    # 최대 굽힘 응력 σ = M×c/I = (qL²/8)×(d/2)/I
    M_Nm = q * span_m ** 2 / 8.0
    c    = depth_m / 2.0
    sigma_MPa = M_Nm * c / I / 1e6

    allowable_defl_mm = span_m / 300.0 * 1000.0

    return BeamResult(
        name              = name,
        material          = material,
        span_m            = span_m,
        width_m           = width_m,
        depth_m           = depth_m,
        gravity           = g,
        load_kN_per_m     = w_total,
        max_deflection_mm = delta_mm,
        max_stress_MPa    = sigma_MPa,
        allowable_defl_mm = allowable_defl_mm,
        safety_factor     = material.comp_MPa / sigma_MPa,
    )


def analyze_ark_hull(
        cubit_cm:  float,
        gravity:   GravityState | None = None,
        wood_load_fraction: float = 0.35,   # 목재 무게 / 총 배수량
        cargo_fraction:     float = 0.40,   # 화물(동물+식량) / 총 배수량
        allowable_MPa:      float = 15.0,   # 목재 허용 굽힘 응력
) -> ArkHullResult:
    """
    노아 방주 선체 구조 분석.
    300×50×30 규빗 기준.
    """
    g = gravity or GRAVITY_PRE_FLOOD  # 방주 = 궁창 시대

    L = 300 * cubit_cm / 100.0   # m
    B = 50  * cubit_cm / 100.0
    H = 30  * cubit_cm / 100.0

    # 배수량: 선체 부피 × 해수 밀도
    # 흘수 추정: 배수량(화물) = 선체 + 화물 무게
    # 단순화: 방주 = 직사각형 바지선 형태
    # 흘수 d = 배수량 / (L × B × ρ_seawater)
    rho_water = 1025.0   # 해수 밀도 (kg/m³)
    rho_wood  = 600.0    # 고페르나무 추정

    # 선체 목재 부피 추정 (껍데기 두께 0.3m 가정)
    t_hull = 0.30   # m, 선체 두께 초기 추정
    V_wood = 2 * (L * B * t_hull     # 상·하 갑판
                  + L * H * t_hull * 2   # 좌·우 현
                  + B * H * t_hull * 2)  # 선수·미
    mass_wood_kg = rho_wood * V_wood
    # 화물 질량: 동물 + 식량 + 사람 (불확실, 비율로 처리)
    # 배수량 = wood / wood_fraction
    displacement_kg = mass_wood_kg / wood_load_fraction
    displacement_t  = displacement_kg / 1000.0

    # 흘수
    draft_m     = displacement_kg / (rho_water * L * B)
    freeboard_m = H - draft_m

    # 호깅 굽힘 모멘트 (단순화 공식)
    # 파고 = L/20 (규칙파 가정), Mh ≈ ρ×g×B×L³/(40π²)
    wave_height = L / 20.0
    M_hog_Nm = rho_water * g.g_ms2 * B * L ** 3 / (40 * math.pi ** 2)
    M_hog_MNm = M_hog_Nm / 1e6

    # 요구 단면 계수 Z = M / σ_allow
    Z_req_m3 = M_hog_Nm / (allowable_MPa * 1e6)

    # 선체 두께 역산 (Z = bh²/6 for rectangle, b=B, solve for h)
    h_req = math.sqrt(6 * Z_req_m3 / B)

    return ArkHullResult(
        cubit_cm           = cubit_cm,
        gravity            = g,
        length_m           = L,
        width_m            = B,
        height_m           = H,
        displacement_t     = displacement_t,
        hogging_moment_MNm = M_hog_MNm,
        required_Z_m3      = Z_req_m3,
        hull_thickness_m   = h_req,
        draft_m            = draft_m,
        freeboard_m        = freeboard_m,
    )


# ── 통합 분석 래퍼 ────────────────────────────────────────────

def full_structure_analysis(
        cubit_cm: float,
        gravity:  GravityState | None = None,
) -> dict:
    """
    주요 성경 구조물 전체 구조 분석.

    Returns:
        dict: {
            "ark": ArkHullResult,
            "jachin": ColumnResult,   # 야긴 기둥
            "boaz": ColumnResult,     # 보아스 기둥
            "holy_of_holies_beam": BeamResult,  # 지성소 지붕 보
            "temple_rafter": BeamResult,
        }
    """
    g = gravity or GRAVITY_MODERN
    cu = cubit_cm / 100.0   # m

    # 야긴·보아스 기둥 (왕상 7:15)
    # 높이 18 규빗, 둘레 12 규빗 → 직경 = 12/(π) 규빗
    col_h = 18 * cu
    col_d = (12 * cu) / math.pi   # 둘레 → 직경
    jachin = analyze_column(
        "야긴 기둥 (Jachin)", MATERIALS["bronze"],
        col_h, col_d, gravity=g, K=2.0
    )
    boaz = analyze_column(
        "보아스 기둥 (Boaz)", MATERIALS["bronze"],
        col_h, col_d, gravity=g, K=2.0
    )

    # 지성소 지붕 보 (20×20 규빗 스팬, 백향목)
    hoh_span = 20 * cu
    hoh_beam = analyze_beam(
        "지성소 지붕 보 (Holy of Holies)",
        MATERIALS["cedar"],
        span_m    = hoh_span,
        width_m   = 0.40,           # 40cm 각재
        depth_m   = 0.60,           # 60cm 깊이
        floor_load_kPa = 3.0,
        gravity   = g,
    )

    # 성소 지붕 보 (40 규빗 스팬)
    temple_span = 40 * cu
    temple_beam = analyze_beam(
        "성소 지붕 보 (Sanctuary)",
        MATERIALS["cedar"],
        span_m    = temple_span,
        width_m   = 0.45,
        depth_m   = 0.80,
        floor_load_kPa = 3.0,
        gravity   = g,
    )

    # 노아 방주
    ark = analyze_ark_hull(cubit_cm, gravity=g)

    return {
        "ark":                 ark,
        "jachin":              jachin,
        "boaz":                boaz,
        "holy_of_holies_beam": hoh_beam,
        "temple_rafter":       temple_beam,
    }
