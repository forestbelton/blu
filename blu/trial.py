import dataclasses

from blu import combat, monster


@dataclasses.dataclass
class CombatTrial:
    player_stats: combat.CombatStats
    monster_stats: list[monster.MonsterStats]
    sample_size: int = dataclasses.field(default=100_000)


def run_trial(trial: CombatTrial) -> None:
    print(f"Player: {trial.player_stats}")

    monster_names = "\n".join(str(monster) for monster in trial.monster_stats)
    print(f"VS:\n{monster_names}")
    print(f"=== {trial.sample_size} trials ===")

    num_monsters = len(trial.monster_stats)

    turn_hists = [{} for _ in range(num_monsters)]
    hp_hists = [{} for _ in range(num_monsters)]
    for _ in range(trial.sample_size):
        player = combat.CombatEntity.from_stats(trial.player_stats)
        for index, monster_stats in enumerate(trial.monster_stats):
            player.stats = player.base_stats
            starting_hp = player.cur_hp
            monster = combat.CombatEntity.from_stats(monster_stats)
            battle_turns = combat.simulate_battle(player, monster)
            turn_hists[index][battle_turns] = turn_hists[index].get(battle_turns, 0) + 1
            hp = starting_hp - player.cur_hp
            hp_hists[index][hp] = hp_hists[index].get(hp, 0) + 1

    total = trial.sample_size
    for index in range(num_monsters):
        print(f"BATTLE #{index}\n---")
        for turns, count in sorted(turn_hists[index].items()):
            print(f"{turns=} {round(count/total*100,2)}% ({count}/{total})")
        print("")
        for hp, count in sorted(hp_hists[index].items()):
            print(f"hp=-{hp} {round(count/total*100,2)}% ({count}/{total})")
        print("---\n")
