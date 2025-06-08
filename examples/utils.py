from poker_engine.action_type import *
def get_player_status_str(player_dict, include_hand: bool) -> str:
    res = [
        f"Player {player_dict["id"]}: Your balance is {player_dict["balance"]}, ",
        f"have spent {player_dict["money_in"]} in this game and have ",
        f'{"" if player_dict["folded"] else "not yet "}' + "folded."
    ]
    if include_hand:
        res.append(f"\nYour hands are {player_dict["hands"][0]}, and {player_dict["hands"][1]}")
    return ''.join(res)

options_map = {
    ActionType.FOLD: "Fold (F)",
    ActionType.ALL_IN: "Go all in (A)",
    ActionType.CALL: "Call on current bet (C)"
}
def get_options_str(options_dict) -> str:
    options = []
    for k, val in options_dict.items():
        if val:
            if k == ActionType.RAISE:
                assert len(val) == 2
                options.append(f"Raise by minimum {val[0]}, maximum {val[1]} (R,V)")
            else:
                options.append(options_map[k])
    return ', '.join(options)

initial_to_ActionType = {
    "F": ActionType.FOLD,
    "R": ActionType.RAISE,
    "C": ActionType.CALL,
    "A": ActionType.ALL_IN
}