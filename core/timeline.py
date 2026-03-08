"""
timeline.py — 성경 인물 시간축 데이터

창세기 5장, 11장, 기타 역사서 수명 기록.
각 인물에 대해 시대(era)에 맞는 CanopyState를 제공.

수명 감소 패턴 (홍수 전후 핵심 전환점):
  홍수 이전: 930, 912, 905, 910, 895, 962, 969, 777, 950 (평균 ~900)
  셈 이후  : 600 → 438 → 239 → 175 → 120 → 70    (지속 감소)
"""

from __future__ import annotations
from dataclasses import dataclass
from .canopy import (CanopyState,
                     CANOPY_PRE_FLOOD, CANOPY_EARLY_POST,
                     CANOPY_PATRIARCHAL, CANOPY_MOSAIC,
                     CANOPY_KINGDOM, CANOPY_MODERN)

_ERA_MAP: dict[str, CanopyState] = {
    "pre_flood":    CANOPY_PRE_FLOOD,
    "early_post":   CANOPY_EARLY_POST,
    "patriarchal":  CANOPY_PATRIARCHAL,
    "mosaic":       CANOPY_MOSAIC,
    "kingdom":      CANOPY_KINGDOM,
    "modern":       CANOPY_MODERN,
}


@dataclass(frozen=True)
class BiblicalPerson:
    """성경 인물 레코드"""
    name:        str       # 영문명
    name_kr:     str       # 한국어
    lifespan_yr: int       # 수명 (년)
    generation:  int       # 아담부터 세대 수
    era:         str       # 시대 코드
    reference:   str       # 성경 참조
    role:        str = ""  # 주요 역할

    @property
    def canopy_state(self) -> CanopyState:
        return _ERA_MAP.get(self.era, CANOPY_MODERN)

    def short(self) -> str:
        return f"{self.name_kr}({self.lifespan_yr}년)"


# ══════════════════════════════════════════════════════════════
# 홍수 이전 계보 (창세기 5장) — 궁창 시대
# ══════════════════════════════════════════════════════════════
PRE_FLOOD_LINEAGE: tuple[BiblicalPerson, ...] = (
    BiblicalPerson("Adam",       "아담",    930, 1,  "pre_flood", "Gen 5:5",   "최초 인간, 흙으로 창조"),
    BiblicalPerson("Seth",       "셋",      912, 2,  "pre_flood", "Gen 5:8",   "아담의 셋째 아들"),
    BiblicalPerson("Enosh",      "에노스",  905, 3,  "pre_flood", "Gen 5:11"),
    BiblicalPerson("Kenan",      "게난",    910, 4,  "pre_flood", "Gen 5:14"),
    BiblicalPerson("Mahalalel",  "마할랄렐",895, 5,  "pre_flood", "Gen 5:17"),
    BiblicalPerson("Jared",      "야렛",    962, 6,  "pre_flood", "Gen 5:20"),
    BiblicalPerson("Enoch",      "에녹",    365, 7,  "pre_flood", "Gen 5:23",  "죽지 않고 승천"),
    BiblicalPerson("Methuselah", "므두셀라",969, 8,  "pre_flood", "Gen 5:27",  "성경 최장수"),
    BiblicalPerson("Lamech",     "라멕",    777, 9,  "pre_flood", "Gen 5:31"),
    BiblicalPerson("Noah",       "노아",    950, 10, "pre_flood", "Gen 9:29",  "방주 건설자, 홍수 생존"),
)

# ══════════════════════════════════════════════════════════════
# 홍수 이후 초기 계보 (창세기 11장) — 수명 급감 구간
# ══════════════════════════════════════════════════════════════
EARLY_POST_LINEAGE: tuple[BiblicalPerson, ...] = (
    BiblicalPerson("Shem",      "셈",      600, 11, "early_post", "Gen 11:10", "노아의 아들"),
    BiblicalPerson("Arphaxad",  "아르박삿",438, 12, "early_post", "Gen 11:13"),
    BiblicalPerson("Shelah",    "셀라",    433, 13, "early_post", "Gen 11:15"),
    BiblicalPerson("Eber",      "에벨",    464, 14, "early_post", "Gen 11:17"),
    BiblicalPerson("Peleg",     "벨렉",    239, 15, "early_post", "Gen 11:19", "땅이 나뉜 시대(바벨탑?)"),
    BiblicalPerson("Reu",       "르우",    239, 16, "early_post", "Gen 11:21"),
    BiblicalPerson("Serug",     "스룩",    230, 17, "early_post", "Gen 11:23"),
)

# ══════════════════════════════════════════════════════════════
# 족장 시대 — 환경 안정화, 수명 200년 이하
# ══════════════════════════════════════════════════════════════
PATRIARCHAL_LINEAGE: tuple[BiblicalPerson, ...] = (
    BiblicalPerson("Nahor",    "나홀",    148, 18, "patriarchal", "Gen 11:25"),
    BiblicalPerson("Terah",    "데라",    205, 19, "patriarchal", "Gen 11:32", "아브라함의 아버지"),
    BiblicalPerson("Abraham",  "아브라함",175, 20, "patriarchal", "Gen 25:7",  "믿음의 조상, 이집트 체류"),
    BiblicalPerson("Isaac",    "이삭",    180, 21, "patriarchal", "Gen 35:28"),
    BiblicalPerson("Jacob",    "야곱",    147, 22, "patriarchal", "Gen 47:28", "이스라엘"),
    BiblicalPerson("Joseph",   "요셉",    110, 23, "patriarchal", "Gen 50:26", "이집트 총리"),
)

# ══════════════════════════════════════════════════════════════
# 모세·성막 시대
# ══════════════════════════════════════════════════════════════
MOSAIC_PERSONS: tuple[BiblicalPerson, ...] = (
    BiblicalPerson("Moses",   "모세",    120, 26, "mosaic", "Deut 34:7",  "성막 건설 지휘, 이집트 규빗 사용"),
    BiblicalPerson("Joshua",  "여호수아",110, 27, "mosaic", "Josh 24:29", "가나안 정복"),
)

# ══════════════════════════════════════════════════════════════
# 왕국 시대 — 성전 건설
# ══════════════════════════════════════════════════════════════
KINGDOM_PERSONS: tuple[BiblicalPerson, ...] = (
    BiblicalPerson("David",   "다윗",   70, 33, "kingdom", "1Kgs 2:11", "성전 설계·재료 준비"),
    BiblicalPerson("Solomon", "솔로몬", 60, 34, "kingdom", "1Kgs 11:42","솔로몬 성전 건설"),
    BiblicalPerson("Ezekiel", "에스겔", 60, 40, "kingdom", "Ezek 1:1",  "성전 환상, 장규빗 명시"),
)

# ══════════════════════════════════════════════════════════════
# 현대 기준점
# ══════════════════════════════════════════════════════════════
MODERN_REFERENCE: tuple[BiblicalPerson, ...] = (
    BiblicalPerson("Modern",  "현대인", 75, 99, "modern", "-", "현재 평균"),
)

ALL_PERSONS: tuple[BiblicalPerson, ...] = (
    PRE_FLOOD_LINEAGE
    + EARLY_POST_LINEAGE
    + PATRIARCHAL_LINEAGE
    + MOSAIC_PERSONS
    + KINGDOM_PERSONS
    + MODERN_REFERENCE
)


def get_person(name: str) -> BiblicalPerson | None:
    """이름(영문 or 한국어)으로 인물 검색"""
    name_lower = name.lower()
    for p in ALL_PERSONS:
        if p.name.lower() == name_lower or p.name_kr == name:
            return p
    return None


def lifespan_at_era(era: str) -> float:
    """해당 시대 인물들의 평균 수명"""
    persons = [p for p in ALL_PERSONS if p.era == era]
    if not persons:
        return 75.0
    return sum(p.lifespan_yr for p in persons) / len(persons)
