"""
scenario_engine.py — 다중 시나리오 비교 엔진

같은 구조물을 여러 규빗 표준으로 계산해 비교.
시대별 규빗 추적 (수명 → 신체 → 규빗 감소 흐름).
"""

from __future__ import annotations
from dataclasses import dataclass
from .core.canopy   import CanopyState, ERA_SEQUENCE
from .core.biology  import estimate_body, BodyProfile
from .core.timeline import ALL_PERSONS, BiblicalPerson, lifespan_at_era
from .units.cubit_standards import (CubitStandard, ALL_STANDARDS,
                                     cubit_from_body, CUBIT_COMMON)
from .structures._base import StructureResult


@dataclass(frozen=True)
class ScenarioRow:
    """시나리오 단일 행"""
    standard:  CubitStandard
    result:    StructureResult

    @property
    def cubit_cm(self) -> float:
        return self.standard.cm


@dataclass(frozen=True)
class ScenarioComparison:
    """여러 규빗 시나리오 비교 결과"""
    structure_name: str
    rows:           tuple[ScenarioRow, ...]

    def table(self) -> str:
        header = (
            f"\n{'규빗 표준':<28} {'cm':>6}  {'길이(m)':>9}  "
            f"{'너비(m)':>9}  {'높이(m)':>9}  {'부피(m³)':>12}\n"
            + "─" * 82
        )
        lines = [header]
        for row in self.rows:
            r = row.result
            dm = r.dims_m
            # 길이/너비/높이 레이블 자동 탐지
            length = next((v for k, v in dm.items() if "길이" in k or "length" in k.lower()), 0)
            width  = next((v for k, v in dm.items() if "너비" in k or "width" in k.lower()), 0)
            height = next((v for k, v in dm.items() if "높이" in k or "height" in k.lower()), 0)
            lines.append(
                f"  {row.standard.name_kr:<26} {row.standard.cm:>6.1f}  "
                f"{length:>9.2f}  {width:>9.2f}  {height:>9.2f}  {r.volume_m3:>12.1f}"
            )
        return "\n".join(lines)


@dataclass(frozen=True)
class TemporalRow:
    """시간축 단일 행"""
    person:   BiblicalPerson
    body:     BodyProfile
    cubit_cm: float


@dataclass(frozen=True)
class TemporalAnalysis:
    """시대별 규빗 추적 결과"""
    rows: tuple[TemporalRow, ...]

    def table(self) -> str:
        header = (
            f"\n{'인물':<10} {'수명':>5}  {'규빗(cm)':>9}  "
            f"{'신장(cm)':>9}  {'스케일':>7}  {'시대':<22}\n"
            + "─" * 80
        )
        lines = [header]
        prev_era = ""
        for row in self.rows:
            if row.person.era != prev_era:
                if prev_era:
                    lines.append("  " + "·" * 60)
                prev_era = row.person.era
            bar = "█" * min(20, int(row.body.scale_factor * 10))
            lines.append(
                f"  {row.person.name_kr:<9} {row.person.lifespan_yr:>5}년  "
                f"{row.cubit_cm:>9.2f}  {row.body.height_cm:>9.1f}  "
                f"{row.body.scale_factor:>7.3f}×  {row.person.era:<22}"
            )
        return "\n".join(lines)

    def cubit_range(self) -> tuple[float, float]:
        vals = [r.cubit_cm for r in self.rows]
        return min(vals), max(vals)


# ── 비교 함수들 ──────────────────────────────────────────────

def compare_scenarios(
        compute_fn,
        standards: tuple[CubitStandard, ...] | None = None
) -> ScenarioComparison:
    """
    여러 규빗 표준으로 같은 구조물 계산 비교.

    Args:
        compute_fn: standard → StructureResult 함수
        standards: 비교할 규빗 표준들 (기본: ALL_STANDARDS)
    """
    stds = standards or ALL_STANDARDS
    rows = tuple(
        ScenarioRow(std, compute_fn(std))
        for std in stds
    )
    name = rows[0].result.structure_name if rows else "?"
    return ScenarioComparison(structure_name=name, rows=rows)


def temporal_analysis(
        compute_fn=None,
        persons: tuple[BiblicalPerson, ...] | None = None,
        model_params: dict | None = None
) -> TemporalAnalysis:
    """
    시대별 인물 → 신체 추정 → 규빗 변화 추적.

    Args:
        compute_fn: (선택) 각 규빗으로 구조물도 계산할 경우
        persons:    분석할 인물들 (기본: ALL_PERSONS)
    """
    targets = persons or ALL_PERSONS
    rows = []
    for person in targets:
        body = estimate_body(
            person.canopy_state,
            person.lifespan_yr,
            model_params
        )
        row = TemporalRow(
            person   = person,
            body     = body,
            cubit_cm = body.cubit_cm,
        )
        rows.append(row)
    return TemporalAnalysis(rows=tuple(rows))


def canopy_sensitivity(
        compute_fn,
        pressure_range:   tuple[float, float] = (1.0, 3.0),
        o2_range:         tuple[float, float] = (0.21, 0.35),
        lifespan:         float = 950.0,
        steps:            int   = 5
) -> list[dict]:
    """
    대기압×산소 범위 감도 분석.
    각 (pressure, o2) 조합에서 신체 스케일과 규빗을 계산.
    """
    from .core.canopy import CanopyState
    from .core.biology import estimate_body

    results = []
    p_step  = (pressure_range[1] - pressure_range[0]) / (steps - 1)
    o2_step = (o2_range[1] - o2_range[0]) / (steps - 1)

    for i in range(steps):
        pressure = pressure_range[0] + i * p_step
        for j in range(steps):
            o2 = o2_range[0] + j * o2_step
            state = CanopyState(
                name         = f"P={pressure:.2f}atm O2={o2*100:.0f}%",
                pressure_atm = pressure,
                o2_fraction  = o2,
                co2_ppm      = 2000.0,
                uv_shield    = 0.95,
                temp_mean_C  = 27.0,
                humidity     = 0.90,
            )
            body = estimate_body(state, lifespan)
            results.append({
                "pressure_atm": pressure,
                "o2_pct":       o2 * 100,
                "cubit_cm":     body.cubit_cm,
                "height_cm":    body.height_cm,
                "scale":        body.scale_factor,
            })
    return results
