from blu import combat, effect

Attack = combat.DamageSkill(
    name="ATTACK",
    power=10,
    type=combat.SkillType.PHYSICAL,
    mp_cost=0,
)

Confuse = combat.EffectSkill(
    name="CONFUSE",
    type=combat.SkillType.MAGIC,
    mp_cost=3,
    effect=effect.Effect.CONFUSION,
    duration_turns=1,
)

# NB: Must be here to avoid circular dependency
combat.DEFAULT_SKILLS = [Attack]
