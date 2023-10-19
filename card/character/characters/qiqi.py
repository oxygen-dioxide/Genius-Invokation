from card.character.base import NormalAttack, ElementalSkill, ElementalBurst
from entity.character import Character
from entity.entity import Entity
from utils import *
from typing import TYPE_CHECKING, List, Tuple
from event.damage import Damage

if TYPE_CHECKING:
    from game.game import GeniusGame
    from game.action import Action
    from event.events import ListenerNode
    from game.player import GeniusPlayer
from entity.status import Status, Combat_Status
from entity.summon import Summon
from loguru import logger

class Ancient_Sword_Art(NormalAttack):
    name = 'Ancient Sword Art'
    id: int = 0
    type: SkillType = SkillType.NORMAL_ATTACK

    # damage
    damage_type: SkillType = SkillType.NORMAL_ATTACK
    main_damage_element: ElementType = ElementType.PHYSICAL
    main_damage: int = 2
    piercing_damage: int = 0

    # cost
    cost = [
        {
            'cost_num': 1,
            'cost_type': CostType.CRYO
        },
        {
            'cost_num': 2,
            'cost_type': CostType.BLACK
        }
    ]
    energy_cost: int = 0
    energy_gain: int = 1

    def __init__(self, from_character: 'Character'):
        super().__init__(from_character)

    def on_call(self, game: 'GeniusGame'):
        super().on_call(game)
        # 处理伤害
        self.resolve_damage(game)
        # 获得能量
        self.gain_energy(game)
        # after skill
        game.manager.invoke(EventType.AFTER_USE_SKILL, game)

class Adeptus_Art_Herald_of_Frost(ElementalSkill):
    id = 1
    name = 'Adeptus Art: Herald of Frost'
    type: SkillType = SkillType.ELEMENTAL_SKILL

    # damage
    damage_type: SkillType = SkillType.ELEMENTAL_SKILL
    main_damage_element: ElementType = ElementType.CRYO
    main_damage: int = 0
    piercing_damage: int = 0

    # cost
    cost = [
        {
            'cost_num': 3,
            'cost_type': CostType.CRYO
        },
    ]
    energy_cost: int = 0
    energy_gain: int = 1

    def __init__(self, from_character: 'Character'):
        super().__init__(from_character)

    def generate_summon(self, game: 'GeniusGame'):
        summon = self.from_character.from_player.summons_zone.has_entity(Herald_of_Frost)
        if summon is None:
            summon = Herald_of_Frost(game, self.from_character.from_player, self.from_character)
            self.from_character.from_player.summons_zone.add_entity(summon)
        else:
            summon.update()
    

    def on_call(self, game: 'GeniusGame'):
        super().on_call(game)
        # 处理伤害
        self.generate_summon(game)
        # 获得能量
        self.gain_energy(game)
        # after skill
        game.manager.invoke(EventType.AFTER_USE_SKILL, game)


class Adeptus_Art_Preserver_of_Fortune(ElementalBurst):
    id = 2
    name = 'Adeptus Art: Preserver of Fortune'
    type: SkillType = SkillType.ELEMENTAL_BURST

    # damage
    damage_type: SkillType = SkillType.ELEMENTAL_BURST
    main_damage_element: ElementType = ElementType.CRYO
    main_damage: int = 3
    piercing_damage: int = 0

    # cost
    cost = [
        {
            'cost_num': 3,
            'cost_type': CostType.CRYO
        }
    ]

    energy_cost: int = 3
    energy_gain: int = 0

    def __init__(self, from_character: 'Character'):
        super().__init__(from_character)
    
    def add_status(self, game: 'GeniusGame'):
        status = self.from_character.from_player.team_combat_status.has_status(Fortune_Preserving_Talisman)
        if status is None:
            status = Fortune_Preserving_Talisman(game, self.from_character.from_player, self.from_character)
            self.from_character.from_player.team_combat_status.add_entity(status)
        else:
            status.update()

    def on_call(self, game: 'GeniusGame'):
        super().on_call(game)
        # 处理伤害
        self.consume_energy(game)
        self.resolve_damage(game)
        self.add_status(game)

        if self.from_character.talent:
            if self.from_character.use_revive <2:
                self.from_character.use_revive += 1
                
                for i in range(3):
                    char = self.from_character.from_player.character_list[i]
                    if not char.is_alive:
                        char.revive(game)
                        char.health_point = 2
    
        game.manager.invoke(EventType.AFTER_USE_SKILL, game)

class Qiqi(Character):
    id = 1108
    name = 'Qiqi'
    element = ElementType.CRYO
    weapon_type = WeaponType.SWORD
    country = CountryType.LIYUE

    init_health_point = 10
    max_health_point = 10
    skill_list = [
        Ancient_Sword_Art,
        Adeptus_Art_Herald_of_Frost,
        Adeptus_Art_Preserver_of_Fortune
    ]
    max_power = 3

    def __init__(self, game: 'GeniusGame', zone, from_player: 'GeniusPlayer', index:int, from_character = None, talent = False):
        super().__init__(game, zone, from_player, index, from_character)
        self.talent = talent
        self.power = 0
        self.use_revive = 0

class Herald_of_Frost(Summon):
    name = 'Herald of Frost'
    element = ElementType.CRYO
    usage = 3
    max_usage = 3

    def __init__(self, game: 'GeniusGame', from_player: 'GeniusPlayer', from_character:'Character'=None):
        super().__init__(game, from_player, from_character)
        self.current_usage = 3
    
    def update(self):
        self.current_usage = max(self.current_usage, self.usage)

    def on_end_phase(self, game: 'GeniusGame'):
        if game.active_player == self.from_player:
            dmg = Damage.create_damage(
                game,
                damage_type=SkillType.SUMMON,
                main_damage_element=self.element,
                main_damage=1,
                piercing_damage=0,
                damage_from=self,
                damage_to=get_opponent_active_character(game),
            )
            game.add_damage(dmg)
            game.resolve_damage()
            self.current_usage -= 1
            if self.current_usage <= 0:
                self.on_destroy(game)

    def after_skill(self, game:'GeniusGame'):
        if game.current_skill.from_character==self.from_character:
            if game.current_skill.type == SkillType.NORMAL_ATTACK:
                max_dmg_taken = 0
                max_taken_char = None
                ls: List[int] = []
                id = self.from_player.active_idx
                for i in range(self.from_player.character_num):
                    ls.append(id)
                    ls += 1
                    if ls >= self.from_player.character_num:
                        ls = 0
                    
                for i in ls:
                    char = self.from_player.character_list[i]
                    dmg_taken = char.max_health_point - char.health_point
                    if dmg_taken > max_dmg_taken:
                        max_dmg_taken = dmg_taken
                        max_taken_char = char
                max_taken_char.heal(1)
    
    def update_listener_list(self):
        self.listeners = [
            (EventType.END_PHASE, ZoneType.SUMMON_ZONE, self.on_end_phase),
            (EventType.AFTER_USE_SKILL, ZoneType.SUMMON_ZONE, self.after_skill)
        ]

class Fortune_Preserving_Talisman(Combat_Status):
    name = 'Fortune-Preserving Talisman'
    id = 1
    usage = 3
    max_usage = 3
    def __init__(self, game: 'GeniusGame', from_player: 'GeniusPlayer', from_character=None):
        super().__init__(game, from_player, from_character)
        self.current_usage = 3
    
    def update(self):
        self.current_usage = max(self.current_usage, self.usage)
    
    def after_skill(self, game: 'GeniusGame'):
        if game.current_skill.from_character.from_player == self.from_player:
            if game.current_skill.from_character.health_point != game.current_skill.from_character.max_health_point:
                game.current_skill.from_character.heal(2)
                self.current_usage -= 1
                if self.current_usage<=0:
                    self.on_destroy(game)
    
    def update_listener_list(self):
        self.listeners = [
            (EventType.AFTER_USE_SKILL, ZoneType.ACTIVE_ZONE, self.after_skill)
        ]