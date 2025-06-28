from .hand_manager import HandManager
from collections.abc import Callable, Generator
from typing import Optional
from .players import *

'''
Rules regarding rounds
In Texas Hold'em, 
there are four rounds of betting: pre-flop, flop, turn, and river
Seating order around table - clockwise
Dealer (D) -> Small Blind (SB) -> Big Blind (BB) -> next player (UTG)
After each game, the D/SB/BB shifts one seat clockwise
Pre-flop: UTG acts first
Post-flop (Flop/Turn/River)
: First remaining player clockwise from the SB (inclusive)
'''
from .cards import Card
from .hand_manager import HandManager

class PokerManager:
    def __init__(self, blinds : list[int],
                 players: list[Player],
                 small_blind_i: int = 0):
        assert len(players) > 1
        assert len(blinds) == 2
        assert HandManager.COMM_CARDS + len(players) * HandManager.PLAYER_CARDS <= Card.DECK_SIZE
        self.players: list[Player] = players
        self.small_blind_player_pos = small_blind_i
        self.blinds = blinds
        self._game_num = 0
    
    @property
    def status(self) -> dict:
        return {
            "players_info": [player.public_status for player in self.players],
            "small_blind_player_pos": self.small_blind_player_pos,
            "blinds": self.blinds,
            "game_num": self._game_num
        }
    
    def advance(self) -> Generator[HandManager, None, None]:
        while len(self.players) > 1:
            new_hand = HandManager(
                self.players,
                self.small_blind_player_pos, self.blinds
            )
            yield new_hand
            self.update_for_new_round()

    def update_for_new_round(self):
        players_temp = self.players
        self.players = []
        next_small_blind: Optional[int] = None
        for i, player in enumerate(players_temp):
            if player.balance != 0:
                if next_small_blind is None and i > self.small_blind_player_pos:
                    next_small_blind = len(self.players)
                player.reset_round()
                self.players.append(player)
        self._game_num += 1
        self.small_blind_player_pos = 0 if next_small_blind is None \
                                        else next_small_blind

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
        for hand in self.advance():
            if on_new_hand:
                on_new_hand(hand.status, self.status)
            while not hand.is_complete():
                if on_round_start:
                    on_round_start(hand.status, self.status)
                curr_round = hand.betting_round()
                state = next(curr_round)
                while True:
                    # The caller must send the user_dict back
                    '''
                    in the callback method where user calls play_game, the player
                    object is inaccessible to user, though that is not true
                    if user uses manual control (see examples)
                    '''
                    player: Player = state["player"]
                    state.pop("player")
                    state["player_status"] = player.public_status
                    state["player_status"]["hands"] = player.hands
                    if on_player_turn_start:
                        on_player_turn_start(state, hand.status, self.status)
                    if isinstance(player, AutonomousPlayer):
                        state.pop("player_status")
                        user_dict = player.make_decision(state, hand.status, self.status)
                    elif on_player_turn is not None:
                        user_dict = on_player_turn(state, hand.status, self.status)
                    else:
                        raise ValueError(f"Player {player.id} has no make_decision method and no callback provided")
                    try:
                        state = curr_round.send(user_dict)
                    except StopIteration as e:
                        last_action = e.value
                        if on_round_end:
                            on_round_end(last_action, hand.status, self.status)
                        break
            if on_hand_end:
                on_hand_end(hand.winners, hand.status, self.status)
