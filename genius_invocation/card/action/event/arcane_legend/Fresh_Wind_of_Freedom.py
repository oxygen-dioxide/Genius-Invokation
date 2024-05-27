from genius_invocation.card.action.base import ActionCard
from genius_invocation.utils import *
from genius_invocation.entity.status import Combat_Status
if TYPE_CHECKING:
    from genius_invocation.game.game import GeniusGame
    from genius_invocation.game.player import GeniusPlayer

class Fresh_Wind_of_Freedom_Entity(Combat_Status):
    id: int = 330004
    name = "Fresh Wind of Freedom"
    name_ch = "自由的新风"
    def __init__(self, game: 'GeniusGame', from_player: 'GeniusPlayer', from_character=None):
        super().__init__(game, from_player, from_character)

    # 更新：大鹤归
    def on_after_skill(self, game:'GeniusGame'):
        if game.active_player_index == self.from_player.index:
            if game.current_skill.from_character == self.from_character:
                self.from_player.change_to_next_character()

    def on_end(self, game:'GeniusGame'):
        if game.active_player_index == self.from_player.index:
           self.on_destroy(game)

    def update_listener_list(self):
        self.listeners = [
            (EventType.AFTER_USE_SKILL, ZoneType.ACTIVE_ZONE, self.on_after_skill),
            (EventType.END_PHASE, ZoneType.ACTIVE_ZONE, self.on_end),
        ]


class Fresh_Wind_of_Freedom(ActionCard):
    id: int = 330004
    name = "Fresh Wind of Freedom"
    name_ch = "自由的新风"
    cost_num = 0
    cost_type = None
    card_type = ActionCardType.EVENT_ARCANE_LEGEND
    def __init__(self) -> None:
        super().__init__()

    def on_played(self, game: 'GeniusGame') -> None:
        game.active_player.team_combat_status.add_entity(Fresh_Wind_of_Freedom_Entity(
            game,
            from_player=game.active_player,
            from_character=None
        ))
    
    def find_target(self, game: 'GeniusGame'):
        if game.active_player.play_arcane_legend:
            return []
        return [1]
