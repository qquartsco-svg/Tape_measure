"""
midos_engine — 성경 계측 단위 탐색 엔진
MIDOS: Biblical Measurement Intelligence & Dimension Operating System

1 규빗(Cubit)은 얼마인가?
  → 팔꿈치에서 손끝까지 = 신체 비례 단위
  → 시대마다 대기 환경과 수명이 달랐다면, 규빗도 달랐다
  → 궁창(raqia) 붕괴 이후 인간 신체 크기 감소 → 규빗 감소

ENGINE_HUB 대칭 구조:
  AVCE  : ρ_water × g × V            = 부력   (정적 유체역학)
  FLEN  : ½ρ_air  × v² × S × CL     = 양력   (동적 유체역학)
  MIDOS : cubit_cm × dim_cubits      = 실제크기 (역사 계측학)

설계 철학:
  stdlib only · frozen dataclass · snapshot dict 호환 · 레이어 분리

빠른 시작:
    from midos_engine import analyze

    r = analyze("Noah")           # 노아 기준 분석
    print(r.cubit.cm)            # 모델 추정 규빗 (cm)
    print(r.ark.dims_m)          # 방주 치수 (m)
    print(r.explain())           # 전체 해설
    print(r.snapshot_updates)   # CookiieBrain 파이프라인 연결
"""

from .why_it_measures import MidosResult, analyze, analyze_by_era
from .core.canopy     import (CanopyState,
                               CANOPY_PRE_FLOOD, CANOPY_EARLY_POST,
                               CANOPY_PATRIARCHAL, CANOPY_MOSAIC,
                               CANOPY_KINGDOM, CANOPY_MODERN)
from .core.biology    import BodyProfile, estimate_body
from .core.timeline   import BiblicalPerson, get_person, ALL_PERSONS
from .units.cubit_standards import (CubitStandard, ALL_STANDARDS,
                                     CUBIT_HYPER, CUBIT_COMMON,
                                     CUBIT_SACRED, CUBIT_EGYPTIAN,
                                     CUBIT_TALMUD_S, CUBIT_TALMUD_L)
from .scenario_engine import (compare_scenarios, temporal_analysis,
                               canopy_sensitivity)
from .validator       import validate, rank_standards, ARCH_RECORDS

__all__ = [
    # 메인 API
    "MidosResult", "analyze", "analyze_by_era",
    # 환경
    "CanopyState",
    "CANOPY_PRE_FLOOD", "CANOPY_EARLY_POST", "CANOPY_PATRIARCHAL",
    "CANOPY_MOSAIC", "CANOPY_KINGDOM", "CANOPY_MODERN",
    # 생물
    "BodyProfile", "estimate_body",
    # 타임라인
    "BiblicalPerson", "get_person", "ALL_PERSONS",
    # 규빗 표준
    "CubitStandard", "ALL_STANDARDS",
    "CUBIT_HYPER", "CUBIT_COMMON", "CUBIT_SACRED",
    "CUBIT_EGYPTIAN", "CUBIT_TALMUD_S", "CUBIT_TALMUD_L",
    # 시나리오
    "compare_scenarios", "temporal_analysis", "canopy_sensitivity",
    # 검증
    "validate", "rank_standards", "ARCH_RECORDS",
]

__version__ = "0.1.0"
__engine__  = "MIDOS"
