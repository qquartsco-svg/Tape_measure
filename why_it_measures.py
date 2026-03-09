"""
why_it_measures.py — MIDOS 통합 분석 엔진

"1 규빗은 얼마인가?" 에 대한 다각도 완전 분석.

파이프라인:
  1. 인물(BiblicalPerson) 선택
  2. 궁창 상태(CanopyState) 적용
  3. 신체 추정 → 규빗 산출 (BodyProfile)
  4. 구조물 계산 (4개 성경 구조물)
  5. 고고학 교차 검증
  6. 시나리오 비교
  7. 종합 해설 출력

AVCE / FLEN / MIDOS 대칭:
  AVCE : ρ_water × g × V            = 부력  (정적)
  FLEN : ½ρ_air  × v² × S × CL     = 양력  (동적)
  MIDOS: cubit_cm × dimension_cubits = 실제 크기 (역사)
"""

from __future__ import annotations
from dataclasses import dataclass, field

from .core.canopy    import CanopyState
from .core.biology   import BodyProfile, estimate_body
from .core.timeline  import BiblicalPerson, get_person, ALL_PERSONS
from .units.cubit_standards import (CubitStandard, ALL_STANDARDS,
                                     cubit_from_body, CUBIT_COMMON)
from .structures._base       import StructureResult
from .structures.noahs_ark   import NoahsArk
from .structures.tabernacle  import Tabernacle
from .structures.solomons_temple  import SolomonsTemple
from .structures.ezekiels_temple  import EzekielsTemple
from .scenario_engine import (ScenarioComparison, TemporalAnalysis,
                               compare_scenarios, temporal_analysis)
from .validator       import ValidationResult, validate, rank_standards


@dataclass(frozen=True)
class MidosResult:
    """통합 분석 결과 (불변)"""
    person:       BiblicalPerson
    canopy:       CanopyState
    body:         BodyProfile
    cubit:        CubitStandard       # 모델 추정 규빗

    # 구조물별 계산 (모델 규빗 적용)
    ark:          StructureResult
    tabernacle:   StructureResult
    temple:       StructureResult
    ezekiel:      StructureResult

    # 비교 분석
    scenarios:    ScenarioComparison   # 여러 규빗으로 방주 비교
    temporal:     TemporalAnalysis     # 시대별 규빗 추적
    validation:   ValidationResult     # 고고학 교차 검증

    # Phase 3 확장 포인트: 추가 구조물을 코드 수정 없이 전달
    # 사용법: MidosResult(..., extra_structures=(("헤롯 성전", result), ...))
    # 접근법: dict(r.extra_structures)["헤롯 성전"]
    extra_structures: tuple[tuple[str, StructureResult], ...] = ()

    @property
    def structures_dict(self) -> dict[str, StructureResult]:
        """extra_structures를 dict로 반환 (Phase 3 편의 접근자)"""
        return dict(self.extra_structures)

    @property
    def summary(self) -> str:
        return (
            f"{self.person.name_kr}({self.person.lifespan_yr}년) | "
            f"규빗={self.cubit.cm:.2f}cm | "
            f"신장={self.body.height_cm:.1f}cm | "
            f"방주={self.ark.dims_m.get('길이(length)', 0):.1f}m"
        )

    def explain(self) -> str:
        sep = "═" * 72
        thin = "─" * 72
        lines = [
            sep,
            "  MIDOS — 1 규빗은 얼마인가?  완전 분석",
            sep,
            "",
            f"▶ 분석 인물: {self.person.name_kr} ({self.person.name})",
            f"  수명: {self.person.lifespan_yr}년  |  세대: {self.person.generation}세대",
            f"  역할: {self.person.role}",
            f"  참조: {self.person.reference}",
            "",
            "━ 1. 대기 환경 (궁창 상태) " + "─" * 44,
            self.canopy.info(),
            "",
            "━ 2. 신체 추정 (환경 × 수명 모델) " + "─" * 37,
            self.body.summary(),
            "",
            "━ 3. 추정 규빗 (모델 역산) " + "─" * 45,
            f"  {self.cubit.cm:.3f} cm",
            f"  = 현대 규빗(44.5cm)의 {self.cubit.cm/44.5:.3f}배",
            f"  근거: {self.cubit.source}",
            f"  신뢰도: {self.cubit.confidence:.0%}  (직접 고고학 증거 없음, 모델 추론)",
            "",
            "━ 4. 구조물 계산 (모델 규빗 적용) " + "─" * 36,
            self.ark.summary(),
            "",
            self.tabernacle.summary(),
            "",
            self.temple.summary(),
            "",
            self.ezekiel.summary(),
            "",
            "━ 5. 시나리오 비교 (방주 × 여러 규빗) " + "─" * 32,
            self.scenarios.table(),
            "",
            "━ 6. 고고학 교차 검증 " + "─" * 48,
            self.validation.report(),
            "",
            "━ 7. 시대별 규빗 추적 " + "─" * 48,
            self.temporal.table(),
            "",
            sep,
            "  결론: 규빗은 시대별 신체 크기에 비례한다.",
            f"  궁창 시대 최대 ~{max(r.cubit_cm for r in self.temporal.rows):.1f}cm",
            f"  현대 고고학 확인값 ~44.5cm",
            sep,
        ]
        return "\n".join(lines)

    @property
    def snapshot_updates(self) -> dict:
        """CookiieBrain 파이프라인 호환 딕셔너리"""
        return {
            "midos.person":        self.person.name,
            "midos.cubit_cm":      self.cubit.cm,
            "midos.body_scale":    self.body.scale_factor,
            "midos.height_cm":     self.body.height_cm,
            "midos.ark_length_m":  self.ark.dims_m.get("길이(length)", 0),
            "midos.canopy_era":    self.canopy.name,
            "midos.arch_score":    self.validation.score,
        }


# ── 메인 분석 함수 ───────────────────────────────────────────

def analyze(
        person_name:  str = "Noah",
        model_params: dict | None = None,
) -> MidosResult:
    """
    인물 이름으로 완전 분석 실행.

    Args:
        person_name:  성경 인물 이름 (영문 or 한국어)
        model_params: 생물 스케일 모델 파라미터 override

    Returns:
        MidosResult
    """
    person = get_person(person_name)
    if person is None:
        # 기본값: 노아
        from .core.timeline import BiblicalPerson as BP
        from .core.canopy import CANOPY_PRE_FLOOD
        person = BP("Noah", "노아", 950, 10, "pre_flood", "Gen 9:29", "방주 건설자")

    canopy = person.canopy_state
    body   = estimate_body(canopy, person.lifespan_yr, model_params)
    cubit  = cubit_from_body(body.cubit_cm,
                              confidence=0.30 if person.era == "pre_flood" else 0.50)

    # 구조물 계산
    ark        = NoahsArk.compute(cubit)
    tab        = Tabernacle.compute(cubit)
    temple     = SolomonsTemple.compute(cubit)
    ezekiel    = EzekielsTemple.compute(cubit)

    # 시나리오: 방주를 여러 규빗으로
    scenarios  = compare_scenarios(NoahsArk.compute)

    # 시대별 추적
    temporal   = temporal_analysis(model_params=model_params)

    # 고고학 검증 (모델 규빗 vs 실측)
    validation = validate(cubit)

    return MidosResult(
        person     = person,
        canopy     = canopy,
        body       = body,
        cubit      = cubit,
        ark        = ark,
        tabernacle = tab,
        temple     = temple,
        ezekiel    = ezekiel,
        scenarios  = scenarios,
        temporal   = temporal,
        validation = validation,
    )


def analyze_by_era(era: str, model_params: dict | None = None) -> MidosResult:
    """시대 코드로 대표 인물 자동 선택해 분석"""
    era_rep = {
        "pre_flood":    "Noah",
        "early_post":   "Shem",
        "patriarchal":  "Abraham",
        "mosaic":       "Moses",
        "kingdom":      "Solomon",
        "modern":       "Modern",
    }
    return analyze(era_rep.get(era, "Noah"), model_params)
