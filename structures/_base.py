"""
_base.py — 성경 구조물 기반 클래스

모든 치수는 "순수 규빗" 으로 저장.
CubitStandard를 주입받아 실제 미터값으로 변환.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class dim:
    """단일 치수 정의 (규빗 단위)"""
    label:     str
    cubits:    float
    reference: str = ""   # 성경 구절


@dataclass(frozen=True)
class StructureResult:
    """구조물 계산 결과"""
    structure_name: str
    cubit_cm:       float
    cubit_source:   str
    dims_m:         dict   # {label: meters}
    dims_cu:        dict   # {label: cubits}
    volume_m3:      float
    area_m2:        float
    notes:          str = ""

    def summary(self, indent: int = 2) -> str:
        pad = " " * indent
        lines = [f"[{self.structure_name}] @ {self.cubit_cm:.2f}cm 규빗"]
        for label, val_m in self.dims_m.items():
            cu = self.dims_cu.get(label, 0)
            lines.append(f"{pad}{label:<20}: {cu:>6.1f}규빗 = {val_m:>8.3f} m")
        if self.volume_m3 > 0:
            lines.append(f"{pad}{'부피':<20}: {self.volume_m3:>8.1f} m³")
        if self.area_m2 > 0:
            lines.append(f"{pad}{'면적':<20}: {self.area_m2:>8.1f} m²")
        return "\n".join(lines)
