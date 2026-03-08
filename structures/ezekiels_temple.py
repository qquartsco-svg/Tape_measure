"""
ezekiels_temple.py — 에스겔 성전 (에스겔 40-48장)

핵심: 에스겔 40:5 — 장규빗(Long Cubit) 명시적 정의
  "그 규빗은 통상 규빗에 한 뼘을 더한 것이더라"
  = 일반 규빗 + 1 테파흐(손바닥) = 44.5 + 7.4 ≈ 51.8~52.5 cm

에스겔 성전 전체 부지: 500×500 장규빗
  52.5cm 기준: 262.5m × 262.5m (예루살렘 구도시 면적에 근접)

학술 논쟁:
  종말론적 해석: 메시아 시대의 이상적 성전 비전
  역사적 해석: 바빌론 포로기 건축 계획안
  바빌로니아 영향: 에스겔이 바빌론 신전 건축 양식 참조
"""

from __future__ import annotations
from ._base import dim, StructureResult
from ..units.cubit_standards import CubitStandard, CUBIT_SACRED

# 에스겔은 항상 장규빗 사용 — 기본값 제공
_DEFAULT = CUBIT_SACRED


class EzekielsTemple:
    """에스겔 성전 계산기 (장규빗 적용)"""
    name     = "에스겔 성전 (Ezekiel 40-48)"
    source   = "에스겔 40-48장"
    era_note = "바빌론 포로기 (BC 593-571). 장규빗(51.8cm) 본문 명시."

    @staticmethod
    def compute(standard: CubitStandard | None = None) -> StructureResult:
        std = standard or _DEFAULT
        cm = std.cm
        to_m = lambda cu: cu * cm / 100.0

        dims_cu = {
            # 외벽 (40:5)
            "외벽 두께":            6.0,
            "외벽 높이":            6.0,
            # 동문 (40:6-16)
            "동문 너비":            6.0,
            "문 전체 길이":        50.0,
            "문 전체 너비":        25.0,
            "문지기 방(각)":        6.0,   # 6×6 규빗
            # 바깥뜰 포장 (40:17)
            "바깥뜰 포장 폭":      50.0,
            # 성전 본체 (41장)
            "성소 길이":           40.0,
            "성소 너비":           20.0,
            "지성소 길이":         20.0,
            "지성소 너비":         20.0,
            "성전 전체 길이":     100.0,
            "성전 전체 너비":     100.0,
            # 안뜰 (40:47)
            "안뜰 길이":          100.0,
            "안뜰 너비":          100.0,
            # 전체 성전 부지 (45:2)
            "거룩한 구역 길이":   500.0,
            "거룩한 구역 너비":   500.0,
            "주변 여백":           50.0,
            # 번제단 (43:13-17)
            "제단 상단 크기":      12.0,
        }
        dims_m = {k: to_m(v) for k, v in dims_cu.items()}

        total_area = to_m(500.0) * to_m(500.0)
        temple_vol = to_m(100.0) * to_m(100.0) * to_m(30.0)  # 추정 높이

        return StructureResult(
            structure_name = "에스겔 성전",
            cubit_cm       = cm,
            cubit_source   = std.name_kr + " (본문 명시)",
            dims_m         = dims_m,
            dims_cu        = dims_cu,
            volume_m3      = temple_vol,
            area_m2        = total_area,
            notes          = (
                f"전체 부지 {to_m(500):.1f}×{to_m(500):.1f}m "
                f"= {total_area/10000:.2f} 헥타르. "
                f"에스겔 40:5 '장규빗' 명시 — 성경 내 유일한 규빗 정의 구절."
            ),
        )
