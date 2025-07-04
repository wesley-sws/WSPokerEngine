"""
Run PYTHONPATH=. python examples/poker_game_manual_control.py from root directory
This file demonstrates how to use the library to create a text-based poker 
application using basic console input and output through manual control.

Manual control allows more flexibility, eg can increase blinds every 10 minutes

General Pattern of use (after creating game: PokerManager):
TODO: Change to adapt to new use

for hand in game.advance():
    <may want to do game.get_status() here>
    while not hand.is_complete():
        <may want to do hand.get_status() here>
        curr_round = hand.betting_round()
        state = next(curr_round)
        while True:
            <note state["lastAction"] is None if and only if this is the first 
                iteration of the while loop>
            <get user input and turn it into a dictionary user_dict>
            try:
                state = curr_round.send(user_dict)
            except StopIteration as e:
                <Note e.value is a lastAction dictionary here>
                break
    assert hand.winners > 0
    <do something about the winners>

Note both the hand and game variables provide a get_status method that can
be called anytime
"""
from poker_engine.poker_manager import PokerManager
from poker_engine.poker_manager_builder import PokerManagerBuilder
from poker_engine.players import *

import utils
players: list[Player] = [
    Player(init_balance)
    for init_balance in [6, 2, 400, 500, 600]    
]
game: PokerManager = \
    PokerManagerBuilder().with_blinds(5, 10).add_players(players).build()
for hand in game.advance():
    game_status = game.status
    print("Game Number", game_status["game_num"])
    for player_stats in game_status["players_info"]:
        print(f"Player {player_stats["id"]} has balance {player_stats["balance"]}")
    print("Small blind player:", game_status["small_blind_player_pos"])
    print("The blinds are:", game_status["blinds"])
    while not hand.is_complete():
        hand_status = hand.status
        print(f"Round Number", hand_status["round_num"])
        comm = hand_status["revealed_comm_cards"]
        print(
            "The Community Cards " +
            "have not been revealed" if len(comm) == 0 else 
            f"are {', '.join(map(str, comm))}"
        )
        for player_dict in game_status["players_info"]:
            print(utils.get_player_status_str(player_dict, False))
        curr_round = hand.betting_round()
        state = next(curr_round)
        while True:
            if (last_action := state["last_action_result"]) is not None:
                print(
                    f"Player {last_action["id"]} has put {last_action["last_put"]} and now has {last_action["new_balance"]}"
                )
            player: Player = state["player"]
            state.pop("player")
            print("Your Turn", utils.get_player_status_str(player.public_status, True))
            print("The current bet is", state["current_bet"])

            if isinstance(player, AutonomousPlayer):
                user_dict = player.make_decision(state, hand.status, game.status)
            else:  
                user_input = input(
                    "Your options are " + 
                    utils.get_options_str(state["options"]) + '\n'
                )
                if user_input[0] not in utils.initial_to_ActionType:
                    raise ValueError
                user_action = utils.initial_to_ActionType[user_input[0]]
                user_dict = {"action": user_action}
                if user_input[0] == "R":
                    user_dict["amount"] = int(user_input[2:])
            try:
                state = curr_round.send(user_dict)
                game_status = game.status
            except StopIteration as e:
                last_action = e.value
                game_status = game.status
                print(
                    f"Player {last_action["id"]} has put {last_action["last_put"]} and now has {last_action["new_balance"]}"
                )
                break
    for winner in hand.winners:
        pot = "Main Pot" if winner["pot_count"] == 0 else f"Side Pot {winner["pot_count"]}"
        if winner["hand_strength"] is None:
            print(
                f"Player {winner['id']} has won {pot} (all other players folded)! " +
                f"Your new balance is {winner['new_balance']}."
            )
        else:
            print(
                f"Player {winner["id"]} has won {pot} with {winner["hand_strength"]}! " +
                f"Your new balance is {winner['new_balance']}."
            )
