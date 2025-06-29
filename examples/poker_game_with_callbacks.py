"""
Run PYTHONPATH=. python examples/poker_game_with_callbacks.py from root directory

This file demonstrates how to use the library to create a text-based poker 
application using basic console input and output through the play_game method
in the PokerManager class.

Note that users can inherit the Player class with a make_decision method to adapt
the decision maker for the player/bot. If this is done for all players,
then the play_game wrapper will work without providing an on_player_turn callback.
"""
from poker_engine.poker_manager import PokerManager
import utils
from poker_engine.action_type import *
from poker_engine import PokerManagerBuilder
from poker_engine.game_runner import GameRunner

# class PlayerCLI(Player):
#     def make_decision(self, _, current_bet, options, last_action):
#         if last_action is not None:
#             print(
#                 f"Player {last_action["id"]} has put {last_action["last_put"]} and now has {last_action["new_balance"]}"
#             )
#         print("Your Turn", utils.get_player_status_str(self.status, True))
#         print("The current bet is", current_bet)
#         user_input = input(
#             "Your options are " + 
#             utils.get_options_str(options) + '\n'
#         )
#         user_dict = {"action": utils.initial_to_ActionType[user_input[0]]}
#         if user_input[0] == "R":
#             user_dict["amount"] = int(user_input[2:])
#         return user_dict

def print_comm_cards(hand_status):
    comm = hand_status["revealed_comm_cards"]
    print("The Community Cards", end=" ")
    print(
        "have not been revealed" if len(comm) == 0 else 
        f"are {', '.join(map(str, comm))}"
    )

def on_new_hand(_, game_status):
    print("Game Number", game_status["game_num"])
    for player_stats in game_status["players_info"]:
        print(f"Player {player_stats["id"]} has balance {player_stats["balance"]}")
    print("Small blind player:", game_status["small_blind_player_pos"])
    print("The blinds are:", game_status["blinds"])

def on_round_start(hand_status, game_status):
    print(f"Round Number", hand_status["round_num"])
    print_comm_cards(hand_status)
    for player_status in game_status["players_info"]:
        print(utils.get_player_status_str(player_status, False))

def on_round_end(last_action, *_):
    print(
        f"Player {last_action["id"]} has put {last_action["last_put"]} and now has {last_action["new_balance"]}"
    )

def on_player_turn_start(state, hand_status, *_):
    if (last_action := state["last_action_result"]) is not None:
        print(
            f"Player {last_action["id"]} has put {last_action["last_put"]} and now has {last_action["new_balance"]}"
        )
    print("Your Turn", utils.get_player_status_str(state["player_status"], True))
    print("The current bet is", state["current_bet"])
    print(f"It's {state["current_bet"] - state["player_status"]["money_in"]}" 
          " to call (or all-in if insufficient funds)")
    print("The pot size is", hand_status["pot_size"])


def on_player_turn(state, *_):
    user_input = input(
        "Your options are " + 
        utils.get_options_str(state["options"]) + '\n'
    )
    user_dict = {"action": utils.initial_to_ActionType[user_input[0]]}
    if user_input[0] == "R":
        user_dict["amount"] = int(user_input[2:])
    return user_dict

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

init_balances: list[int] = [200, 300, 400, 500, 600]    
game: PokerManager = \
    PokerManagerBuilder().with_blinds(5, 10).add_players_by_balance(init_balances).build()
runner: GameRunner = GameRunner(game)
runner.play_game(
    on_new_hand=on_new_hand,
    on_player_turn=on_player_turn,
    on_round_start=on_round_start,
    on_round_end=on_round_end,
    on_hand_end=on_hand_end,
    on_player_turn_start=on_player_turn_start
)