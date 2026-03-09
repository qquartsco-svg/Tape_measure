"""
validator.py — 고고학 실측치 교차 검증

알려진 고고학 측정값과 모델 출력을 비교해
각 규빗 시나리오의 신뢰도 점수를 산출.

핵심 데이터:
  실로암 터널 (BC 701): "1200 규빗" → 실측 533m
    → 규빗 = 533/1200 = 44.42 cm
  아랏(Arad) 성소 내부: 10×10 규빗 → 실측 4.45m
    → 규빗 = 44.5 cm
  이집트 왕실 규빗봉: 실물 52.5 cm (투린 박물관)
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from .units.cubit_standards import CubitStandard


@dataclass(frozen=True)
class ArchRecord:
    """고고학 측정 기록"""
    name:         str    # 유물/유적 이름
    measured_m:   float  # 실측값 (m)
    cubits_ref:   float  # 성경/기록의 규빗 수
    implied_cm:   float  # 역산 규빗 (= measured_m×100 / cubits_ref)
    period:       str    # 시대
    source:       str    # 출처
    reliability:  float  # 데이터 신뢰도 0~1

    def implied_cubit_cm(self) -> float:
        divisor = self.cubits_ref if self.cubits_ref > 0 else 1.0
        return self.measured_m * 100.0 / divisor


@dataclass(frozen=True)
class ValidationResult:
    """단일 규빗 표준에 대한 검증 결과"""
    standard:      CubitStandard
    records:       tuple[ArchRecord, ...]
    errors_pct:    tuple[float, ...]    # 각 기록과의 오차 (%)
    avg_error_pct: float
    score:         float                # 종합 점수 0~1 (낮은 오차 = 높은 점수)

    def report(self) -> str:
        lines = [
            f"[검증] {self.standard.name_kr} ({self.standard.cm:.1f}cm)",
            f"  종합 점수   : {self.score:.3f} / 1.0",
            f"  평균 오차   : {self.avg_error_pct:.2f}%",
            "  ─── 항목별 ─────────────────────────────",
        ]
        for rec, err in zip(self.records, self.errors_pct):
            ok = "✓" if abs(err) < 5.0 else ("△" if abs(err) < 15.0 else "✗")
            lines.append(
                f"  {ok} {rec.name:<28} "
                f"역산={rec.implied_cubit_cm():.1f}cm  "
                f"오차={err:+.1f}%"
            )
        return "\n".join(lines)


# ── 고고학 기준 데이터셋 ─────────────────────────────────────

ARCH_RECORDS: tuple[ArchRecord, ...] = (
    ArchRecord(
        name        = "실로암 터널 (히스기야, BC701)",
        measured_m  = 533.0,
        cubits_ref  = 1200.0,
        implied_cm  = 44.42,
        period      = "Iron Age II",
        source      = "Siloam Inscription + Gill(1996) 실측",
        reliability = 0.90,
    ),
    ArchRecord(
        name        = "아랏 성소 내부 (BC10-6c)",
        measured_m  = 4.45,
        cubits_ref  = 10.0,
        implied_cm  = 44.5,
        period      = "Iron Age",
        source      = "Herzog et al. (1984) BASOR 254",
        reliability = 0.82,
    ),
    ArchRecord(
        name        = "이집트 왕실 규빗봉 (투린 박물관)",
        measured_m  = 0.525,
        cubits_ref  = 1.0,
        implied_cm  = 52.5,
        period      = "New Kingdom Egypt",
        source      = "Turin Museum, Maya's cubit rod",
        reliability = 0.98,
    ),
    ArchRecord(
        name        = "헤롯 성전산 남벽 (실측)",
        measured_m  = 280.0,
        cubits_ref  = 600.0,   # 요세푸스 6스타디온 → 2000규빗(추정)
        implied_cm  = 46.7,
        period      = "Herodian (BC 20 ~ AD 70)",
        source      = "Benjamin Mazar 발굴 (1968-78) + 현재 GPS 측량",
        reliability = 0.70,    # 규빗 수 추정치 사용
    ),
    ArchRecord(
        name        = "라기스 궁전 너비 (BC9-8c)",
        measured_m  = 17.80,
        cubits_ref  = 40.0,
        implied_cm  = 44.5,
        period      = "Iron Age II",
        source      = "Usishkin 발굴, Ussishkin (1983)",
        reliability = 0.72,
    ),
)


# ── 검증 함수 ────────────────────────────────────────────────

def validate(
        standard: CubitStandard,
        records:  tuple[ArchRecord, ...] | None = None
) -> ValidationResult:
    """규빗 표준을 고고학 기록과 비교 검증"""
    recs = records or ARCH_RECORDS
    errors = []
    for rec in recs:
        implied = rec.implied_cubit_cm()
        if implied <= 0:
            errors.append(0.0)
            continue
        err_pct = (standard.cm - implied) / implied * 100.0
        errors.append(err_pct)

    # 가중 평균 오차 (reliability 가중)
    weights = [r.reliability for r in recs]
    w_total = sum(weights)
    avg_err = sum(abs(e) * w for e, w in zip(errors, weights)) / w_total

    # 점수: 0% 오차 = 1.0, 20% 오차 = 0.0 (선형)
    score = max(0.0, 1.0 - avg_err / 20.0)

    return ValidationResult(
        standard      = standard,
        records       = recs,
        errors_pct    = tuple(errors),
        avg_error_pct = avg_err,
        score         = score,
    )


def rank_standards(
        standards: tuple[CubitStandard, ...],
        records:   tuple[ArchRecord, ...] | None = None
) -> list[ValidationResult]:
    """모든 표준을 검증하고 점수 순으로 정렬"""
    results = [validate(s, records) for s in standards]
    return sorted(results, key=lambda r: -r.score)
