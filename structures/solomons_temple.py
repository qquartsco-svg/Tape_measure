"""
solomons_temple.py — 솔로몬 성전 (열왕기상 6-7장)

주요 치수 (규빗):
  성전 본체  : 60×20×30 규빗 (현관 포함 70×20)
  지성소(DBR): 20×20×20 규빗 (완전한 정육면체 — 신학적 완전성)
  성소(HKL) : 40×20×30 규빗
  기둥(야긴/보아스): 높이 18 규빗, 둘레 12 규빗
  놋바다(야모): 직경 10, 높이 5, 둘레 30 규빗 (π≈3 이슈)

시대 맥락:
  솔로몬 시대 (BC 966-959 건설). 히람(페니키아)이 기술 지원.
  역대하 3:3 "다윗이 정한 규빗 법도대로" — 왕실 규빗 가능성.
  직접 발굴 불가 (성전산 현재 이슬람 성역).
"""

from __future__ import annotations
from ._base import dim, StructureResult
from ..units.cubit_standards import CubitStandard


class SolomonsTemple:
    """솔로몬 성전 계산기"""
    name     = "솔로몬 성전 (1 Kings 6-7)"
    source   = "열왕기상 6-7장"
    era_note = "솔로몬 시대 (BC 966-959). 히람(두로)과 협력. 직접 발굴 불가."

    @staticmethod
    def compute(standard: CubitStandard) -> StructureResult:
        cm = standard.cm
        to_m = lambda cu: cu * cm / 100.0

        dims_cu = {
            # 성전 본체 (6:2-3)
            "성전 전체 길이":       60.0,
            "성전 전체 너비":       20.0,
            "성전 전체 높이":       30.0,
            "현관(울람) 길이":      10.0,
            "현관 너비":            20.0,
            # 지성소 (6:20) — 정육면체
            "지성소 길이":          20.0,
            "지성소 너비":          20.0,
            "지성소 높이":          20.0,
            # 성소 (6:17)
            "성소 길이":            40.0,
            # 측면 방 (6:5-6)
            "측면방 1층 너비":       5.0,
            "측면방 2층 너비":       6.0,
            "측면방 3층 너비":       7.0,
            # 기둥 야긴/보아스 (7:15-22)
            "기둥 높이":            18.0,
            "기둥 둘레":            12.0,
            "주두(Chapiter) 높이":   5.0,
            # 놋바다 (7:23-26)
            "놋바다 직경":          10.0,
            "놋바다 높이":           5.0,
            "놋바다 둘레":          30.0,
        }
        dims_m = {k: to_m(v) for k, v in dims_cu.items()}

        L = to_m(60.0)
        W = to_m(20.0)
        H = to_m(30.0)

        notes = (
            f"놋바다 π체크: 둘레={to_m(30.0):.2f}m / 직경={to_m(10.0):.2f}m = "
            f"{30.0/10.0:.4f} (성경), 실제 π={3.14159:.4f}. "
            f"지성소는 완전한 정육면체({to_m(20.0):.1f}m³ 한 변)."
        )

        return StructureResult(
            structure_name = "솔로몬 성전",
            cubit_cm       = cm,
            cubit_source   = standard.name_kr,
            dims_m         = dims_m,
            dims_cu        = dims_cu,
            volume_m3      = L * W * H,
            area_m2        = L * W,
            notes          = notes,
        )
