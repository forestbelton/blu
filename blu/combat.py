import abc
import collections
import dataclasses
import enum
import random

from blu import effect

DEFAULT_SKILLS: list["Skill"] = []
DEFAULT_SKILL_DENOMINATOR = 100


@dataclasses.dataclass
class CombatStats:
    watk: int
    wdef: int
    matk: int
    mdef: int

    max_hp: int
    max_mp: int

    skills: list["Skill"] = dataclasses.field(default_factory=lambda: DEFAULT_SKILLS)
    skill_distribution: list[int] = dataclasses.field(
        default_factory=lambda: [DEFAULT_SKILL_DENOMINATOR]
    )
    skill_distribution_denominator = DEFAULT_SKILL_DENOMINATOR


TurnCount = int


@dataclasses.dataclass
class CombatEntity:
    stats: CombatStats
    base_stats: CombatStats

    cur_hp: int
    cur_mp: int

    effects: dict[effect.Effect, TurnCount] = dataclasses.field(
        default_factory=lambda: collections.defaultdict(lambda: 0)
    )

    @staticmethod
    def from_stats(stats: CombatStats) -> "CombatEntity":
        return CombatEntity(
            stats=dataclasses.replace(stats),
            base_stats=stats,
            cur_hp=stats.max_hp,
            cur_mp=stats.max_mp,
        )


class SkillType(enum.Enum):
    PHYSICAL = "PHYSICAL"
    MAGIC = "MAGIC"


@dataclasses.dataclass
class Skill(abc.ABC):
    name: str
    type: SkillType
    mp_cost: int

    def can_use(self, source: CombatEntity, target: CombatEntity) -> bool:
        return source.cur_mp >= self.mp_cost

    # TODO: Return list of effects (informational)
    @abc.abstractmethod
    def apply(self, source: CombatEntity, target: CombatEntity) -> int: ...


@dataclasses.dataclass
class DamageSkill(Skill):
    power: int = dataclasses.field(default=0)

    def get_damage(self, source: CombatEntity, target: CombatEntity) -> int:
        base_damage = 1
        match self.type:
            case SkillType.PHYSICAL:
                base_damage = max(1, source.stats.watk - target.stats.wdef // 2)
            case SkillType.MAGIC:
                base_damage = max(1, source.stats.matk - target.stats.mdef // 2)
        # TODO: Scale based on skill power
        variance = max(1, base_damage // 10)
        random_damage = base_damage + random.randint(0, 2 * variance) - variance
        return max(1, random_damage)

    def apply(self, source: CombatEntity, target: CombatEntity) -> int:
        damage = self.get_damage(source, target)
        target.cur_hp = max(0, target.cur_hp - damage)
        return damage


@dataclasses.dataclass
class EffectSkill(Skill):
    effect: effect.Effect
    duration_turns: int

    def apply(self, source: CombatEntity, target: CombatEntity) -> int:
        target.effects[self.effect] = max(
            target.effects.get(self.effect, 0),
            self.duration_turns,
        )
        return 0


@dataclasses.dataclass
class CoinFlipSkill(Skill):
    bias: int
    skill: Skill

    def apply(self, source: CombatEntity, target: CombatEntity) -> int:
        result = 0
        probability = random.randint(1, 100)
        if probability <= self.bias:
            result = self.skill.apply(source, target)
        return result


def simulate_turn_target(source: CombatEntity, target: CombatEntity) -> None:
    actual_target = target
    if source.effects[effect.Effect.CONFUSION] > 0 and random.randint(0, 1) == 0:
        actual_target = source
    choice = random.randint(1, source.stats.skill_distribution_denominator)
    chosen_skill = source.stats.skills[0]
    for skill_index, probability in enumerate(source.stats.skill_distribution):
        skill = source.stats.skills[skill_index]
        if choice <= probability and skill.can_use(source, actual_target):
            chosen_skill = skill
            break
        choice -= probability
    assert chosen_skill.can_use(source, actual_target)
    chosen_skill.apply(source, actual_target)
    source.cur_mp = max(0, source.cur_mp - chosen_skill.mp_cost)
    # NB: Leaves in effects once they don't apply. Doesn't matter.
    remove_effects = []
    for source_effect, turns_left in source.effects.items():
        source.effects[source_effect] = turns_left - 1
        if source.effects[source_effect] == 0:
            remove_effects.append(source_effect)
    for source_effect in remove_effects:
        del source.effects[source_effect]


def simulate_battle(source: CombatEntity, target: CombatEntity) -> int:
    turns = 0
    while source.cur_hp > 0 and target.cur_hp > 0:
        simulate_turn_target(source, target)
        if target.cur_hp > 0:
            simulate_turn_target(target, source)
        turns += 1
    return turns
