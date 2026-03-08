"""
run_midos_demo.py — MIDOS 엔진 실행 데모

사용법:
    python run_midos_demo.py              # 전체 데모
    python run_midos_demo.py --person Noah
    python run_midos_demo.py --person 아브라함
    python run_midos_demo.py --era pre_flood
    python run_midos_demo.py --temporal    # 시대별 규빗 추적
    python run_midos_demo.py --validate    # 고고학 검증
    python run_midos_demo.py --sensitivity # 대기 감도 분석
    python run_midos_demo.py --all
"""

import sys
import os

# 패키지 경로 설정
_HERE   = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from midos_engine import (
    analyze, analyze_by_era,
    compare_scenarios, temporal_analysis, canopy_sensitivity,
    rank_standards, ALL_STANDARDS, ARCH_RECORDS,
    CANOPY_PRE_FLOOD, CANOPY_EARLY_POST, CANOPY_PATRIARCHAL,
    CANOPY_MOSAIC, CANOPY_KINGDOM, CANOPY_MODERN,
    estimate_body, ALL_PERSONS,
)
from midos_engine.structures.noahs_ark import NoahsArk
from midos_engine.structures.solomons_temple import SolomonsTemple
from midos_engine.units.cubit_standards import CUBIT_COMMON, CUBIT_SACRED, CUBIT_HYPER


# ── 데모 섹션들 ──────────────────────────────────────────────

def demo_canopy():
    """궁창 시대 대기 환경 비교"""
    sep = "═" * 72
    print(f"\n{sep}")
    print("  1. 궁창(Raqia) 대기 상태 시뮬레이션")
    print(sep)
    for state in [CANOPY_PRE_FLOOD, CANOPY_EARLY_POST,
                  CANOPY_PATRIARCHAL, CANOPY_MOSAIC, CANOPY_MODERN]:
        print(state.info())


def demo_body_scale():
    """시대별 신체 크기 추정"""
    sep = "═" * 72
    print(f"\n{sep}")
    print("  2. 신체 크기 추정 (환경 × 수명 모델)")
    print(sep)
    test_cases = [
        (CANOPY_PRE_FLOOD,    950, "노아 (방주 건설자)"),
        (CANOPY_EARLY_POST,   600, "셈 (노아의 아들)"),
        (CANOPY_PATRIARCHAL,  175, "아브라함"),
        (CANOPY_MOSAIC,       120, "모세 (성막 건설)"),
        (CANOPY_MODERN,        75, "현대인 (기준)"),
    ]
    for canopy, lifespan, label in test_cases:
        body = estimate_body(canopy, lifespan)
        bar = "█" * int(body.scale_factor * 5) + "░" * max(0, 10 - int(body.scale_factor * 5))
        print(
            f"  {label:<20} | 수명 {lifespan:>3}년 | "
            f"신장 {body.height_cm:>6.1f}cm | "
            f"규빗 {body.cubit_cm:>6.2f}cm | "
            f"스케일 {body.scale_factor:.3f}× {bar}"
        )


def demo_temporal():
    """시대별 규빗 감소 전체 추적"""
    sep = "═" * 72
    print(f"\n{sep}")
    print("  3. 시대별 규빗 추적 (수명 감소 → 규빗 감소)")
    print(sep)
    ta = temporal_analysis()
    print(ta.table())
    lo, hi = ta.cubit_range()
    print(f"\n  범위: {lo:.2f}cm ~ {hi:.2f}cm  (현대 대비 {hi/lo:.1f}배 변동)")


def demo_ark_scenarios():
    """노아 방주 × 여러 규빗 시나리오"""
    sep = "═" * 72
    print(f"\n{sep}")
    print("  4. 노아 방주 (창 6:15) — 규빗 시나리오 비교")
    print(sep)
    sc = compare_scenarios(NoahsArk.compute)
    print(sc.table())
    print()
    print("  [ 비교 기준 ]")
    print(f"  타이타닉     : 269.0 m")
    print(f"  현대 컨테이너선(대형): 400 m")


def demo_full_analysis():
    """노아 기준 완전 분석"""
    sep = "═" * 72
    print(f"\n{sep}")
    print("  5. 완전 분석 — 노아 (궁창 시대)")
    print(sep)
    r = analyze("Noah")
    print(r.explain())


def demo_moses():
    """모세 기준 분석 (성막 시대)"""
    sep = "═" * 72
    print(f"\n{sep}")
    print("  6. 모세 분석 — 성막 시대 규빗")
    print(sep)
    r = analyze("Moses")
    print(f"  모세 추정 규빗: {r.cubit.cm:.2f} cm")
    print(f"  현대 기준 44.5cm 대비: {r.cubit.cm/44.5:.3f}배")
    print(f"  이집트 왕실 규빗(52.5cm) 대비: {r.cubit.cm/52.5:.3f}배")
    print()
    print("  성막 주요 치수:")
    for k, v in r.tabernacle.dims_m.items():
        cu = r.tabernacle.dims_cu.get(k, 0)
        print(f"    {k:<20}: {cu:>5.1f}규빗 = {v:>7.3f} m")


def demo_validation():
    """고고학 교차 검증"""
    sep = "═" * 72
    print(f"\n{sep}")
    print("  7. 고고학 교차 검증 — 규빗 표준 신뢰도 랭킹")
    print(sep)
    ranked = rank_standards(ALL_STANDARDS, ARCH_RECORDS)
    print(f"  {'순위':<4} {'표준명':<28} {'cm':>6}  {'점수':>6}  {'평균오차':>8}")
    print("  " + "─" * 60)
    for i, res in enumerate(ranked, 1):
        print(
            f"  {i:<4} {res.standard.name_kr:<28} "
            f"{res.standard.cm:>6.1f}  "
            f"{res.score:>6.3f}  "
            f"{res.avg_error_pct:>7.2f}%"
        )


def demo_sensitivity():
    """대기 감도 분석"""
    sep = "═" * 72
    print(f"\n{sep}")
    print("  8. 감도 분석 — 대기압 × 산소 농도 → 규빗 변화 (수명 950년 고정)")
    print(sep)
    results = canopy_sensitivity(
        compute_fn    = None,
        pressure_range = (1.0, 3.0),
        o2_range      = (0.21, 0.35),
        lifespan      = 950.0,
        steps         = 4
    )
    print(f"  {'기압(atm)':<12} {'산소(%)':>8}  {'규빗(cm)':>10}  {'신장(cm)':>10}  {'스케일':>8}")
    print("  " + "─" * 56)
    for r in results:
        print(
            f"  {r['pressure_atm']:<12.2f} {r['o2_pct']:>8.1f}  "
            f"{r['cubit_cm']:>10.2f}  {r['height_cm']:>10.1f}  {r['scale']:>8.3f}"
        )


def demo_gravity():
    """중력·대기 구조 하중 분석"""
    from midos_engine.core.gravity import (
        gravity_from_canopy, atmospheric_load,
        GRAVITY_PRE_FLOOD, GRAVITY_MODERN
    )
    sep = "═" * 72
    print(f"\n{sep}")
    print("  10. 중력 및 대기 구조 하중 — 궁창 시대 vs 현대")
    print(sep)
    print(GRAVITY_PRE_FLOOD.info())
    print(GRAVITY_MODERN.info())

    print("  [ 설계 풍속 30m/s 기준 바람 동압 비교 ]")
    for canopy_name, canopy in [
        ("궁창 시대", CANOPY_PRE_FLOOD),
        ("족장 시대", CANOPY_PATRIARCHAL),
        ("현대",      CANOPY_MODERN),
    ]:
        al = atmospheric_load(canopy, wind_speed_ms=30.0)
        print(
            f"  {canopy_name:<10}: "
            f"ρ={al.gravity.air_density:.3f}kg/m³  "
            f"동압={al.wind_dynamic_pressure:.1f}Pa  "
            f"(현재의 {al.wind_pressure_ratio:.2f}배)"
        )


def demo_structure_analysis():
    """솔로몬 성전 구조 안전 검증"""
    from midos_engine.structures.load_analysis import full_structure_analysis, GRAVITY_MODERN
    from midos_engine.units.cubit_standards import CUBIT_COMMON, CUBIT_HYPER
    sep = "═" * 72
    print(f"\n{sep}")
    print("  11. 솔로몬 성전 구조 하중 분석")
    print(sep)
    for std_name, cu_cm in [("일반 규빗 44.5cm", 44.5), ("하이퍼 규빗 90.0cm", 90.0)]:
        print(f"\n  ── {std_name} ──")
        checks = full_structure_analysis(cu_cm, GRAVITY_MODERN)
        for item in checks.values():
            if hasattr(item, "report"):
                print(item.report())


def demo_temple_full():
    """솔로몬 성전 상세 설계"""
    from midos_engine.structures.solomons_temple_full import analyze_temple
    from midos_engine.units.cubit_standards import CUBIT_COMMON, CUBIT_HYPER, CUBIT_SACRED
    sep = "═" * 72
    print(f"\n{sep}")
    print("  12. 솔로몬 성전 상세 설계 — 규빗 3-way 비교")
    print(sep)
    for std in [CUBIT_COMMON, CUBIT_SACRED, CUBIT_HYPER]:
        result = analyze_temple(std)
        print(result.summary())


def demo_growth_models():
    """멱함수 vs 로지스틱 성장 모델 비교"""
    from midos_engine.core.biology import estimate_body
    sep = "═" * 72
    print(f"\n{sep}")
    print("  13. 성장 모델 비교 — 멱함수 vs 로지스틱")
    print(sep)
    print(f"  {'인물':<10} {'수명':>5}  {'멱함수(cm)':>10}  {'로지스틱(cm)':>12}  {'차이':>8}")
    print("  " + "─" * 54)
    test_cases = [
        ("노아",     950, CANOPY_PRE_FLOOD),
        ("셈",       600, CANOPY_EARLY_POST),
        ("아브라함", 175, CANOPY_PATRIARCHAL),
        ("모세",     120, CANOPY_MOSAIC),
        ("솔로몬",    60, CANOPY_MODERN),
        ("현대인",    75, CANOPY_MODERN),
    ]
    for name, lifespan, canopy in test_cases:
        b_pow = estimate_body(canopy, lifespan, growth_model="power")
        b_log = estimate_body(canopy, lifespan, growth_model="logistic")
        diff  = b_log.cubit_cm - b_pow.cubit_cm
        print(
            f"  {name:<10} {lifespan:>5}년  "
            f"{b_pow.cubit_cm:>10.2f}  "
            f"{b_log.cubit_cm:>12.2f}  "
            f"{diff:>+8.2f}"
        )


def demo_unit_system():
    """규빗별 히브리 단위 체계"""
    sep = "═" * 72
    print(f"\n{sep}")
    print("  9. 히브리 단위 체계 비교")
    print(sep)
    from midos_engine.units.conversions import CubitConverter
    for std in [CUBIT_HYPER, CUBIT_SACRED, CUBIT_COMMON]:
        conv = CubitConverter(std)
        print(conv.table())


# ── 메인 ────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    run_all = "--all" in args or not args

    if "--canopy" in args or run_all:
        demo_canopy()

    if "--body" in args or run_all:
        demo_body_scale()

    if "--temporal" in args or run_all:
        demo_temporal()

    if "--ark" in args or run_all:
        demo_ark_scenarios()

    if "--validate" in args or run_all:
        demo_validation()

    if "--sensitivity" in args or run_all:
        demo_sensitivity()

    if "--units" in args or run_all:
        demo_unit_system()

    if "--gravity" in args or run_all:
        demo_gravity()

    if "--structure" in args or run_all:
        demo_structure_analysis()

    if "--temple" in args or run_all:
        demo_temple_full()

    if "--growth" in args or run_all:
        demo_growth_models()

    if "--person" in args:
        idx = args.index("--person")
        name = args[idx + 1] if idx + 1 < len(args) else "Noah"
        r = analyze(name)
        print(r.explain())

    elif "--era" in args:
        idx = args.index("--era")
        era = args[idx + 1] if idx + 1 < len(args) else "pre_flood"
        r = analyze_by_era(era)
        print(r.explain())

    elif "--full" in args or run_all:
        demo_full_analysis()
        demo_moses()


if __name__ == "__main__":
    main()
