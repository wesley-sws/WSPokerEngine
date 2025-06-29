from .poker_manager import PokerManager
from .players import *
from typing import Callable, Optional
class GameRunner:
    def __init__(self, poker_manager: PokerManager):
        self.game: PokerManager = poker_manager
    def play_game(
        self,
        on_player_turn: Callable[[dict, dict, dict], dict] = None,
        on_player_turn_start: Callable[[dict, dict, dict], None] = None,
        on_new_hand: Optional[Callable[[dict, dict], None]] = None,
        on_round_start: Optional[Callable[[dict, dict], None]] = None,
        on_round_end: Optional[Callable[[dict, dict, dict], None]] = None,
        on_hand_end: Optional[Callable[[dict, dict, dict], None]] = None,
    ):
        '''
        Convenience wrapper (limited control)
        '''
        for hand in self.game.advance():
            if on_new_hand:
                on_new_hand(hand.status, self.game.status)
            while not hand.is_complete():
                if on_round_start:
                    on_round_start(hand.status, self.game.status)
                curr_round = hand.betting_round()
                state = next(curr_round)
                while True:
                    # The caller must send the user_dict back
                    '''
                    in the callback method where user calls play_self.game, the player
                    object is inaccessible to user, though that is not true
                    if user uses manual control (see examples)
                    '''
                    player: Player = state["player"]
                    state.pop("player")
                    state["player_status"] = player.public_status
                    state["player_status"]["hands"] = player.hands
                    if on_player_turn_start:
                        on_player_turn_start(state, hand.status, self.game.status)
                    if isinstance(player, AutonomousPlayer):
                        state.pop("player_status")
                        user_dict = player.make_decision(state, hand.status, self.game.status)
                    elif on_player_turn is not None:
                        user_dict = on_player_turn(state, hand.status, self.game.status)
                    else:
                        raise ValueError(f"Player {player.id} has no make_decision method and no callback provided")
                    try:
                        state = curr_round.send(user_dict)
                    except StopIteration as e:
                        last_action = e.value
                        if on_round_end:
                            on_round_end(last_action, hand.status, self.game.status)
                        break
            if on_hand_end:
                on_hand_end(hand.winners, hand.status, self.game.status)