import dataclasses

from blu import combat, skill


@dataclasses.dataclass
class MonsterStats(combat.CombatStats):
    name: str = ""
    exp: int = dataclasses.field(default=0)


BAT = MonsterStats(
    name="BAT",
    watk=1,
    wdef=0,
    matk=0,
    mdef=0,
    max_hp=4,
    max_mp=6,
    skills=[skill.Attack, skill.Confuse],
    skill_distribution=[75, 25],
    exp=2,
)

SCORPION = None
SALAMANDER = None
ALMIRAJ = None
SANDMAN = None
ROC = None
DJINN = None
BASTET = None
