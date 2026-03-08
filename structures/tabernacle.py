"""
tabernacle.py — 성막(Tabernacle) + 성물 (출애굽기 25-27장)

구조물 치수 (규빗):
  성막 본체    : 30×10×10 규빗 (길이×너비×높이)
  뜰(Courtyard): 100×50 규빗
  법궤(Ark)    : 2½×1½×1½ 규빗
  진설병 상    : 2×1×1½ 규빗
  번제단       : 5×5×3 규빗
  분향단       : 1×1×2 규빗

시대 맥락:
  모세 시대 (BC 1446). 이집트 체류 후 → 이집트 단위 영향 가능.
  그러나 출애굽 후 → 독자적 히브리 규빗 사용 주장도 있음.
"""

from __future__ import annotations
from ._base import dim, StructureResult
from ..units.cubit_standards import CubitStandard


class Tabernacle:
    """성막 계산기"""
    name     = "성막 (Tabernacle, Exo 25-27)"
    source   = "출애굽기 25-27장"
    era_note = "모세 시대 (BC 1446). 이집트 규빗 또는 히브리 규빗."

    @staticmethod
    def compute(standard: CubitStandard) -> StructureResult:
        cm = standard.cm
        to_m = lambda cu: cu * cm / 100.0

        # 뜰 (가장 큰 구조)
        court_L, court_W = 100.0, 50.0

        dims_cu = {
            # 성막 본체
            "성막 길이":         30.0,
            "성막 너비":         10.0,
            "판자 높이":         10.0,
            "성소 길이":         20.0,
            "지성소 길이":       10.0,
            # 뜰
            "뜰 길이(N/S)":     100.0,
            "뜰 너비(E/W)":      50.0,
            "포장 높이":          5.0,
            # 법궤
            "법궤 길이":          2.5,
            "법궤 너비":          1.5,
            "법궤 높이":          1.5,
            # 진설병 상
            "진설병상 길이":       2.0,
            "진설병상 너비":       1.0,
            "진설병상 높이":       1.5,
            # 번제단
            "번제단 길이":         5.0,
            "번제단 너비":         5.0,
            "번제단 높이":         3.0,
            # 분향단
            "분향단 길이":         1.0,
            "분향단 높이":         2.0,
        }
        dims_m = {k: to_m(v) for k, v in dims_cu.items()}

        vol = to_m(30.0) * to_m(10.0) * to_m(10.0)  # 성막 본체
        area = to_m(court_L) * to_m(court_W)

        return StructureResult(
            structure_name = "성막",
            cubit_cm       = cm,
            cubit_source   = standard.name_kr,
            dims_m         = dims_m,
            dims_cu        = dims_cu,
            volume_m3      = vol,
            area_m2        = area,
            notes          = "람세스 2세 이동식 신전(이집트)과 구조 유사성 존재.",
        )
