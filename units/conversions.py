"""
conversions.py — 규빗 기반 단위 변환

히브리 단위 체계: etzba < tefach < zeret < amah < qaneh
  1 amah(규빗) = 2 zeret(뼘) = 6 tefach(손바닥) = 24 etzba(손가락)
  1 qaneh(갈대) = 6 amah
  1 mil(랍비) = 2000 amah
"""

from __future__ import annotations
from dataclasses import dataclass
from .cubit_standards import CubitStandard


@dataclass(frozen=True)
class CubitConverter:
    """규빗 기반 단위 변환기"""
    standard: CubitStandard

    # ── 기본 변환 ────────────────────────────────────────────

    def cubits_to_m(self, cubits: float) -> float:
        return cubits * self.standard.cm / 100.0

    def cubits_to_cm(self, cubits: float) -> float:
        return cubits * self.standard.cm

    def cubits_to_ft(self, cubits: float) -> float:
        return self.cubits_to_m(cubits) * 3.28084

    def m_to_cubits(self, meters: float) -> float:
        return meters * 100.0 / self.standard.cm

    # ── 히브리 하위 단위 ──────────────────────────────────────

    def etzba_cm(self) -> float:     return self.standard.cm / 24.0
    def tefach_cm(self) -> float:    return self.standard.cm / 6.0
    def zeret_cm(self) -> float:     return self.standard.cm / 2.0
    def qaneh_cm(self) -> float:     return self.standard.cm * 6.0
    def mil_m(self) -> float:        return self.standard.cm * 2000 / 100.0

    # ── 구조물 3D 계산 ───────────────────────────────────────

    def box_m(self, length_cu: float, width_cu: float, height_cu: float
              ) -> tuple[float, float, float]:
        """(길이, 너비, 높이) in meters"""
        return (self.cubits_to_m(length_cu),
                self.cubits_to_m(width_cu),
                self.cubits_to_m(height_cu))

    def volume_m3(self, l_cu: float, w_cu: float, h_cu: float) -> float:
        l, w, h = self.box_m(l_cu, w_cu, h_cu)
        return l * w * h

    def area_m2(self, l_cu: float, w_cu: float) -> float:
        return self.cubits_to_m(l_cu) * self.cubits_to_m(w_cu)

    def table(self) -> str:
        c = self.standard.cm
        return (
            f"[{self.standard.name_kr}] 단위 환산표\n"
            f"  에츠바(손가락, 1/24규빗)  : {c/24:.3f} cm\n"
            f"  테파흐(손바닥, 1/6 규빗)  : {c/6:.3f} cm\n"
            f"  제레트(뼘,     1/2 규빗)  : {c/2:.3f} cm\n"
            f"  아마  (규빗,   기준)       : {c:.3f} cm\n"
            f"  카네  (갈대,   6규빗)      : {c*6:.3f} cm  ({c*6/100:.3f} m)\n"
            f"  밀    (랍비 마일, 2000규빗): {c*2000/100:.1f} m\n"
        )


def hebrews_unit_system(cubit_cm: float) -> dict[str, float]:
    """규빗 값으로 전체 단위 체계 딕셔너리 반환 (cm 기준)"""
    return {
        "etzba_cm":  cubit_cm / 24.0,
        "tefach_cm": cubit_cm / 6.0,
        "zeret_cm":  cubit_cm / 2.0,
        "amah_cm":   cubit_cm,
        "qaneh_cm":  cubit_cm * 6.0,
        "mil_m":     cubit_cm * 2000 / 100.0,
    }
