from blu import combat, monster, trial


def main():
    lv1_player_stats = combat.CombatStats(
        watk=2, wdef=1, matk=1, mdef=1, max_hp=10, max_mp=10
    )
    bat_trial = trial.CombatTrial(
        player_stats=lv1_player_stats,
        monster_stats=[monster.BAT],
    )
    trial.run_trial(bat_trial)


if __name__ == "__main__":
    main()
