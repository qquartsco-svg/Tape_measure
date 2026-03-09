"""
tests/test_midos.py — MIDOS 엔진 기본 검증 테스트

실행:
    python midos_engine/tests/test_midos.py          # 직접 실행
    python -m pytest midos_engine/tests/             # pytest 사용 시
"""

from __future__ import annotations
import sys
import os
import warnings

# 패키지 루트를 경로에 추가 (Tape_measure/ 에서 실행 시)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from midos_engine import analyze
from midos_engine.core.canopy import CANOPY_MODERN, CANOPY_PRE_FLOOD
from midos_engine.core.biology import estimate_body, compute_body_scale
from midos_engine.units.conversions import CubitConverter
from midos_engine.units.cubit_standards import CUBIT_COMMON, CUBIT_HYPER
from midos_engine.validator import validate


# ══════════════════════════════════════════════════════════════
# 1. biology.py — 신체 스케일 모델
# ══════════════════════════════════════════════════════════════

def test_modern_baseline():
    """현대 기준값: scale ≈ 1.0, 규빗 ≈ 44.5cm"""
    body = estimate_body(CANOPY_MODERN, lifespan_yr=75.0)
    assert abs(body.scale_factor - 1.0) < 0.02, \
        f"현대 scale이 1.0이어야 함: {body.scale_factor:.4f}"
    assert abs(body.cubit_cm - 44.5) < 1.0, \
        f"현대 규빗이 44.5cm 근처여야 함: {body.cubit_cm:.2f}"


def test_preflood_exceeds_modern():
    """궁창 시대 scale이 현대의 1.5배 이상"""
    body = estimate_body(CANOPY_PRE_FLOOD, lifespan_yr=950.0)
    assert body.scale_factor > 1.5, \
        f"Pre-flood scale이 1.5 이상이어야 함: {body.scale_factor:.4f}"


def test_scale_monotone_by_lifespan():
    """수명이 길수록 scale이 단조 증가 (같은 환경 기준)"""
    lifespans = [75, 120, 175, 600, 950]
    scales = [estimate_body(CANOPY_MODERN, l).scale_factor for l in lifespans]
    for i in range(len(scales) - 1):
        assert scales[i] <= scales[i + 1], (
            f"수명 증가 시 scale 감소: "
            f"{lifespans[i]}yr→{scales[i]:.4f}, {lifespans[i+1]}yr→{scales[i+1]:.4f}"
        )


def test_scale_warning_threshold():
    """scale > 2.5 시 UserWarning 발생"""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        estimate_body(CANOPY_PRE_FLOOD, lifespan_yr=9999.0)
        assert any(issubclass(x.category, UserWarning) for x in w), \
            "scale 초과 시 UserWarning이 발생해야 함"


def test_invalid_lifespan():
    """lifespan <= 0 은 ValueError"""
    try:
        estimate_body(CANOPY_MODERN, lifespan_yr=0)
        assert False, "ValueError가 발생해야 함"
    except ValueError:
        pass


def test_logistic_vs_power():
    """로지스틱 모델이 멱함수보다 높은 scale 반환 (수명 950년 기준)"""
    body_pow = estimate_body(CANOPY_PRE_FLOOD, 950, growth_model="power")
    body_log = estimate_body(CANOPY_PRE_FLOOD, 950, growth_model="logistic")
    assert body_log.scale_factor > body_pow.scale_factor, \
        f"로지스틱 scale이 멱함수보다 커야 함: {body_log.scale_factor:.3f} vs {body_pow.scale_factor:.3f}"


# ══════════════════════════════════════════════════════════════
# 2. conversions.py — 단위 변환
# ══════════════════════════════════════════════════════════════

def test_converter_round_trip():
    """m → 규빗 → m 왕복 변환 정확도"""
    conv = CubitConverter(CUBIT_COMMON)
    m = 133.5
    cubits = conv.m_to_cubits(m)
    back = conv.cubits_to_m(cubits)
    assert abs(back - m) < 1e-9, f"왕복 변환 오차: {back - m}"


def test_converter_zero_division_guard():
    """ZeroDivisionError 방지 — 비정상 표준 감지"""
    from midos_engine.units.cubit_standards import CubitStandard
    bad_std = CubitStandard(
        name="Bad", name_kr="오류", cm=0.0,
        source="test", period="test", confidence=0.0, context="test"
    )
    conv = CubitConverter(bad_std)
    try:
        conv.m_to_cubits(1.0)
        assert False, "ValueError가 발생해야 함"
    except ValueError:
        pass


# ══════════════════════════════════════════════════════════════
# 3. validator.py — 고고학 검증
# ══════════════════════════════════════════════════════════════

def test_common_cubit_high_score():
    """일반 규빗(44.5cm) 고고학 검증 점수 ≥ 0.70
    (헤롯 성전 46.7cm 포함 5개 기록 가중 평균 — 완벽 일치 불가)"""
    result = validate(CUBIT_COMMON)
    assert result.score >= 0.70, \
        f"일반 규빗 검증 점수가 0.70 이상이어야 함: {result.score:.3f}"


def test_hyper_cubit_low_score():
    """하이퍼 규빗(89.5cm)은 현대 고고학 기록과 맞지 않아 점수 낮아야 함"""
    result = validate(CUBIT_HYPER)
    assert result.score < 0.50, \
        f"하이퍼 규빗 점수가 0.50 미만이어야 함: {result.score:.3f}"


# ══════════════════════════════════════════════════════════════
# 4. why_it_measures.py — 통합 파이프라인
# ══════════════════════════════════════════════════════════════

def test_analyze_noah_cubit():
    """노아 분석: 규빗 > 50cm, 방주 길이 > 200m"""
    r = analyze("Noah")
    assert r.cubit.cm > 50, f"노아 규빗이 50cm 이상이어야 함: {r.cubit.cm:.2f}"
    ark_len = r.ark.dims_m.get("길이(length)", 0)
    assert ark_len > 200, f"방주 길이가 200m 이상이어야 함: {ark_len:.1f}"


def test_analyze_modern_cubit():
    """현대인 분석: 규빗이 44.5cm ± 2cm 범위"""
    r = analyze("Modern")
    assert abs(r.cubit.cm - 44.5) < 2.0, \
        f"현대 규빗이 44.5cm 근처여야 함: {r.cubit.cm:.2f}"


def test_analyze_abraham_vs_egypt():
    """아브라함 규빗 — 이집트 왕실 규빗(52.5cm)과 10% 이내"""
    r = analyze("Abraham")
    egypt_cm = 52.5
    diff_pct = abs(r.cubit.cm - egypt_cm) / egypt_cm * 100
    assert diff_pct < 10.0, \
        f"아브라함 규빗({r.cubit.cm:.2f}cm)이 이집트 규빗(52.5cm)과 10% 초과 차이: {diff_pct:.1f}%"


def test_midos_result_extra_structures():
    """extra_structures 확장 필드 기본값 및 접근"""
    r = analyze("Noah")
    assert r.extra_structures == (), "extra_structures 기본값은 빈 tuple"
    assert isinstance(r.structures_dict, dict), "structures_dict는 dict 반환"


def test_unknown_person_fallback():
    """존재하지 않는 인물명 → 노아로 fallback (예외 없음)"""
    r = analyze("존재하지않는인물XYZ")
    assert r.person.name in ("Noah", "Modern"), \
        f"알 수 없는 인물은 Noah 또는 Modern으로 fallback 해야 함: {r.person.name}"


# ══════════════════════════════════════════════════════════════
# 실행기
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tests = [
        # biology
        test_modern_baseline,
        test_preflood_exceeds_modern,
        test_scale_monotone_by_lifespan,
        test_scale_warning_threshold,
        test_invalid_lifespan,
        test_logistic_vs_power,
        # conversions
        test_converter_round_trip,
        test_converter_zero_division_guard,
        # validator
        test_common_cubit_high_score,
        test_hyper_cubit_low_score,
        # pipeline
        test_analyze_noah_cubit,
        test_analyze_modern_cubit,
        test_analyze_abraham_vs_egypt,
        test_midos_result_extra_structures,
        test_unknown_person_fallback,
    ]

    passed = failed = 0
    print("\n" + "═" * 60)
    print("  MIDOS 테스트 실행")
    print("═" * 60)
    for t in tests:
        try:
            t()
            print(f"  ✓  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗  {t.__name__}")
            print(f"       → {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗  {t.__name__}  (예외: {type(e).__name__}: {e})")
            failed += 1

    print("─" * 60)
    print(f"  결과: {passed}/{passed+failed} 통과  |  {failed} 실패")
    print("═" * 60)
    sys.exit(0 if failed == 0 else 1)
