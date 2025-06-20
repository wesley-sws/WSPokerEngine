"""
Run PYTHONPATH=. python examples/poker_game_with_callbacks.py from root directory

This file demonstrates how to use the library to create a text-based poker 
application using basic console input and output through the play_game method
in the PokerManager class.
"""
from poker_engine.poker_manager import PokerManager
import utils
from poker_engine.action_type import *

def print_comm_cards(hand_status):
    comm = hand_status["revealed_comm_cards"]
    print("The Community Cards", end=" ")
    print(
        "have not been revealed" if len(comm) == 0 else 
        f"are {', '.join(map(str, comm))}"
    )

def on_new_hand(_, game_status):
    print("Game Number", game_status["game_num"])
    for (id, balance) in game_status["players_info"]:
        print(f"Player {id} has balance {balance}")
    print("Small blind player:", game_status["small_blind_player_i"])
    print("The blinds are:", game_status["blinds"])

def on_round_start(hand_status, _):
    print(f"Round Number", hand_status["round_num"])
    print_comm_cards(hand_status)
    for player_dict in hand_status["players_status"]:
        print(utils.get_player_status_str(player_dict, False))

def on_player_turn(state, *_):
    if (last_action := state["last_action_result"]) is not None:
        print(
            f"Player {last_action["id"]} has put {last_action["last_put"]} and now has {last_action["new_balance"]}"
        )
    print("Your Turn", utils.get_player_status_str(state["player_status"], True))
    print("The current bet is", state["current_bet"])
    user_input = input(
        "Your options are " + 
        utils.get_options_str(state["options"]) + '\n'
    )
    user_dict = {"action": utils.initial_to_ActionType[user_input[0]]}
    if user_input[0] == "R":
        user_dict["amount"] = int(user_input[2:])
    return user_dict

def on_round_end(last_action, *_):
    print(
        f"Player {last_action["id"]} has put {last_action["last_put"]} and now has {last_action["new_balance"]}"
    )

def on_hand_end(winners, hand_status, _):
    print_comm_cards(hand_status)
    for winner in winners:
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

# Assuming PokerManager is properly initialized
game = PokerManager([5, 10], [6, 2, 400, 500, 600])
game.play_game(
    on_player_turn=on_player_turn,
    on_new_hand=on_new_hand,
    on_round_start=on_round_start,
    on_round_end=on_round_end,
    on_hand_end=on_hand_end
)