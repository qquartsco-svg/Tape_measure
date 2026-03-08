"""
noahs_ark.py — 노아 방주 (창세기 6:15)

원문: "그 방주의 제도는 이러하니 길이는 삼백 규빗, 너비는 오십 규빗,
      높이는 삼십 규빗이라"

핵심 포인트:
  - 300×50×30 규빗의 선폭비(L/W) = 6:1 → 현대 조선공학적으로 안정 설계
  - 노아 = 궁창 시대 사람 → 하이퍼 규빗 가능성
  - 하이퍼 규빗 적용 시 타이타닉 수준의 거대 선박
"""

from __future__ import annotations
from ._base import dim, StructureResult
from ..units.cubit_standards import CubitStandard

# 원문 치수 (규빗)
LENGTH_CU  = 300.0  # 길이
WIDTH_CU   =  50.0  # 너비
HEIGHT_CU  =  30.0  # 높이
FLOORS     =   3    # 층수 (창 6:16 "위, 중, 아래 칸")

_DIMS = [
    dim("길이(length)",  LENGTH_CU,  "Gen 6:15"),
    dim("너비(width)",   WIDTH_CU,   "Gen 6:15"),
    dim("높이(height)",  HEIGHT_CU,  "Gen 6:15"),
    dim("층고(per floor)", HEIGHT_CU / FLOORS, "Gen 6:16"),
]


class NoahsArk:
    """노아 방주 계산기"""
    name     = "노아 방주 (Gen 6:15)"
    source   = "창세기 6:15"
    era_note = "궁창 시대 (Pre-Flood). 노아 수명 950년. 하이퍼 규빗 적용 권장."

    @staticmethod
    def compute(standard: CubitStandard) -> StructureResult:
        cm = standard.cm
        to_m = lambda cu: cu * cm / 100.0

        L = to_m(LENGTH_CU)
        W = to_m(WIDTH_CU)
        H = to_m(HEIGHT_CU)
        vol = L * W * H

        dims_m  = {d.label: to_m(d.cubits) for d in _DIMS}
        dims_cu = {d.label: d.cubits       for d in _DIMS}
        dims_m["선폭비(L/W)"] = L / W
        dims_cu["선폭비(L/W)"] = LENGTH_CU / WIDTH_CU

        notes = (
            f"타이타닉(269m) 대비: {L/269*100:.0f}%  |  "
            f"현대 대형 화물선(150-200m) 대비: {L/175*100:.0f}%  |  "
            f"선폭비 {L/W:.1f}:1 (현대 조선공학 권장 6~7:1)"
        )

        return StructureResult(
            structure_name = "노아 방주",
            cubit_cm       = cm,
            cubit_source   = standard.name_kr,
            dims_m         = dims_m,
            dims_cu        = dims_cu,
            volume_m3      = vol,
            area_m2        = L * W,
            notes          = notes,
        )
