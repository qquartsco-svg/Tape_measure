"""
solomons_temple_full.py — 솔로몬 성전 상세 설계 분석

열왕기상 6-7장 + 역대하 3-4장 전체 치수 통합.
현대 규빗 / 왕국 시대 규빗 / 하이퍼 규빗 3-way 비교.
구조 공학 분석 포함.

성전 구조 (안에서 밖으로):
  1. 지성소(DBR/Holy of Holies)  — 20×20×20 규빗 정육면체
  2. 성소(HKL/Sanctuary)         — 40×20×30 규빗
  3. 현관(ULAM/Porch)            — 10×20×120 규빗 (역대하 3:4)
  4. 측실(YATSIA/Side Chambers)  — 3층
  5. 야긴·보아스 기둥             — 각 높이 18 + 주두 5 = 23 규빗
  6. 바깥뜰(Outer Court)
  7. 놋바다(Molten Sea)           — 직경 10, 높이 5, 용량 2000밧
  8. 번제단(Altar)                — 20×20×10 규빗 (역대하 4:1)
  9. 물두멍(Lavers) 10개         — 각 직경 4, 높이 6 규빗

재료 목록:
  외벽: 다듬은 석회암
  내부: 백향목 판자 + 올리브나무 조각
  지성소: 순금 도금 (600 달란트 = 약 22.3톤)
  기둥: 청동
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from ..units.cubit_standards import CubitStandard, CUBIT_COMMON, CUBIT_SACRED
from .load_analysis import (
    full_structure_analysis, MATERIALS, analyze_column, analyze_beam,
    GRAVITY_MODERN, GRAVITY_PRE_FLOOD
)
from ..core.gravity import GravityState


@dataclass(frozen=True)
class TempleRoom:
    """성전 단일 공간 치수"""
    name:     str
    name_kr:  str
    L_cu:     float    # 길이 (규빗)
    W_cu:     float    # 너비 (규빗)
    H_cu:     float    # 높이 (규빗)
    material: str      # 재료
    reference: str

    def dims_m(self, cu_m: float) -> tuple[float, float, float]:
        return L_cu * cu_m, W_cu * cu_m, H_cu * cu_m

    def volume_m3(self, cu_m: float) -> float:
        L, W, H = self.L_cu * cu_m, self.W_cu * cu_m, self.H_cu * cu_m
        return L * W * H


@dataclass(frozen=True)
class TempleFullResult:
    """솔로몬 성전 상세 분석 결과"""
    cubit_standard:  CubitStandard
    cubit_cm:        float

    # 공간 치수 (m)
    holy_of_holies:  dict    # 지성소
    sanctuary:       dict    # 성소
    porch:           dict    # 현관
    total_area_m2:   float
    total_volume_m3: float

    # 재료 소요량
    cedar_volume_m3:  float
    gold_mass_kg:     float    # 금 도금 (지성소)
    bronze_mass_kg:   float    # 청동 (기둥+놋바다)
    limestone_mass_kg: float   # 석회암 (외벽)

    # 기물 치수 (m)
    jachin_height_m:   float
    boaz_height_m:     float
    pillar_diameter_m: float
    sea_diameter_m:    float
    sea_volume_m3:     float   # 놋바다 실제 용량
    altar_area_m2:     float

    # 구조 분석
    structure_checks: dict

    def summary(self) -> str:
        c = self.cubit_cm
        hoh = self.holy_of_holies
        san = self.sanctuary
        sep = "─" * 64
        return (
            f"\n{'═'*64}\n"
            f"  솔로몬 성전 상세 설계  [{self.cubit_standard.name_kr}, {c:.1f}cm]\n"
            f"{'═'*64}\n"
            f"\n【공간 구성】\n"
            f"  지성소(Holy of Holies): "
            f"{hoh['L']:.2f}m × {hoh['W']:.2f}m × {hoh['H']:.2f}m\n"
            f"    → 정육면체 {hoh['L']:.2f}m³ 한 변 | 신학적 완전성\n"
            f"  성소  (Sanctuary)     : "
            f"{san['L']:.2f}m × {san['W']:.2f}m × {san['H']:.2f}m\n"
            f"  현관  (Porch/Ulam)    : "
            f"{self.porch['L']:.2f}m × {self.porch['W']:.2f}m\n"
            f"  전체 면적             : {self.total_area_m2:.1f} m²\n"
            f"  전체 부피             : {self.total_volume_m3:.0f} m³\n"
            f"\n{sep}\n"
            f"【기둥 야긴·보아스】\n"
            f"  높이       : {self.jachin_height_m:.2f} m "
            f"(주두 포함 {self.jachin_height_m + self.boaz_height_m:.2f}m)\n"
            f"  직경       : {self.pillar_diameter_m:.2f} m\n"
            f"\n【놋바다(Molten Sea)】\n"
            f"  직경       : {self.sea_diameter_m:.2f} m\n"
            f"  실제 용량  : {self.sea_volume_m3:.1f} m³ "
            f"({self.sea_volume_m3*1000:.0f} 리터)\n"
            f"  성경 기록  : 2000 밧 "
            f"(1밧 ≈ 22L → {2000*22:.0f}L)\n"
            f"  π 이슈     : 직경={self.sea_diameter_m:.2f}m, "
            f"둘레={self.sea_diameter_m*3:.2f}m(×3) vs "
            f"{self.sea_diameter_m*math.pi:.2f}m(×π)\n"
            f"\n{sep}\n"
            f"【재료 소요량】\n"
            f"  백향목     : {self.cedar_volume_m3:.1f} m³\n"
            f"  금(도금)   : {self.gold_mass_kg:.0f} kg "
            f"({self.gold_mass_kg/1000:.1f} 톤)\n"
            f"  청동       : {self.bronze_mass_kg:.0f} kg "
            f"({self.bronze_mass_kg/1000:.1f} 톤)\n"
            f"  석회암(벽) : {self.limestone_mass_kg/1000:.0f} 톤\n"
            f"\n{sep}\n"
            f"【구조 안전 검증】\n"
            + self._struct_report()
        )

    def _struct_report(self) -> str:
        lines = []
        for name, check in self.structure_checks.items():
            if hasattr(check, "report"):
                lines.append(check.report())
        return "\n".join(lines)


def analyze_temple(
        standard:  CubitStandard = CUBIT_COMMON,
        gravity:   GravityState | None = None,
) -> TempleFullResult:
    """솔로몬 성전 전체 상세 분석"""
    g   = gravity or GRAVITY_MODERN
    cm  = standard.cm
    cu  = cm / 100.0   # m per cubit

    # ── 공간 치수 ────────────────────────────────────────────
    hoh = {"L": 20*cu, "W": 20*cu, "H": 20*cu}      # 지성소
    san = {"L": 40*cu, "W": 20*cu, "H": 30*cu}      # 성소
    por = {"L": 10*cu, "W": 20*cu, "H": min(120*cu, 60*cu)}  # 현관 (역대하 3:4 120규빗 논란)

    total_L_m    = (20 + 40 + 10) * cu   # 지성소+성소+현관
    total_area   = total_L_m * (20 * cu)
    total_volume = (hoh["L"]*hoh["W"]*hoh["H"]
                    + san["L"]*san["W"]*san["H"]
                    + por["L"]*por["W"]*min(por["H"], 15*cu))

    # ── 기둥 야긴·보아스 (왕상 7:15-22) ─────────────────────
    col_h  = 18 * cu            # 높이 18 규빗
    col_d  = (12 * cu) / math.pi  # 둘레 12 규빗 → 직경
    cap_h  = 5  * cu            # 주두 높이 5 규빗
    col_total_h = col_h + cap_h

    # ── 놋바다 (왕상 7:23-26) ────────────────────────────────
    sea_d  = 10 * cu            # 직경 10 규빗
    sea_h  = 5  * cu            # 높이 5 규빗
    sea_vol = math.pi * (sea_d/2)**2 * sea_h   # 원통 최대 용량

    # ── 번제단 (역대하 4:1) ──────────────────────────────────
    alt_L = alt_W = 20 * cu
    alt_H = 10 * cu
    altar_area = alt_L * alt_W

    # ── 재료 소요량 ──────────────────────────────────────────

    # 백향목: 내부 판자 (두께 0.1m 가정, 전 내벽)
    inner_surface = (
        2 * san["L"] * san["H"]       # 성소 좌우 벽
        + 2 * san["W"] * san["H"]     # 성소 앞뒤 벽
        + san["L"] * san["W"]         # 성소 천장
        + 2 * hoh["L"] * hoh["H"] * 2  # 지성소
        + hoh["L"] * hoh["W"]
    )
    cedar_volume = inner_surface * 0.08   # 8cm 두께 판자

    # 금 도금: 지성소 전체 (왕상 6:20-22, 역대하 3:8 → 600 달란트)
    # 600 달란트 × 34.27 kg/달란트 = 20,562 kg (성경 기록)
    gold_mass = 600 * 34.27   # kg

    # 청동: 기둥 2개 + 놋바다
    pillar_vol = math.pi * (col_d/2)**2 * col_h * 2
    sea_bronze_vol = math.pi * ((sea_d/2)**2 - (sea_d/2 - 0.08)**2) * sea_h
    bronze_mass = (pillar_vol + sea_bronze_vol) * 8800

    # 석회암 외벽 (두께 2m 가정)
    outer_perimeter = 2 * (total_L_m + 20*cu)
    wall_vol = outer_perimeter * 30*cu * 2.0
    limestone_mass = wall_vol * 2400

    # ── 구조 분석 ─────────────────────────────────────────────
    structure_checks = full_structure_analysis(cm, g)

    return TempleFullResult(
        cubit_standard   = standard,
        cubit_cm         = cm,
        holy_of_holies   = hoh,
        sanctuary        = san,
        porch            = por,
        total_area_m2    = total_area,
        total_volume_m3  = total_volume,
        cedar_volume_m3  = cedar_volume,
        gold_mass_kg     = gold_mass,
        bronze_mass_kg   = bronze_mass,
        limestone_mass_kg= limestone_mass,
        jachin_height_m  = col_h,
        boaz_height_m    = col_h,
        pillar_diameter_m= col_d,
        sea_diameter_m   = sea_d,
        sea_volume_m3    = sea_vol,
        altar_area_m2    = altar_area,
        structure_checks = structure_checks,
    )
