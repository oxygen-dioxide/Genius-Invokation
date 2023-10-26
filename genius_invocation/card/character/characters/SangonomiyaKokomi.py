from genius_invocation.card.character.import_head import *

class The_Shape_of_Water(NormalAttack):
    name = 'The Shape of Water'
    name_ch = '水有常形'
    id = 120501
    type: SkillType = SkillType.NORMAL_ATTACK
    damage_type: SkillType = SkillType.NORMAL_ATTACK
    main_damage_element: ElementType = ElementType.HYDRO
    main_damage: int = 1
    piercing_damage: int = 0
    cost = [{'cost_num':1, 'cost_type':CostType.HYDRO}, {'cost_num':2, "cost_type":CostType.BLACK}]
    energy_cost: int = 0
    energy_gain: int = 1

    def on_call(self, game: 'GeniusGame'):
        super().on_call(game)
        self.resolve_damage(game)
        self.gain_energy(game)
        game.manager.invoke(EventType.AFTER_USE_SKILL, game)


class Kurages_Oath(ElementalSkill):
    name = "Kurage's Oath"
    name_ch = "海月之誓"
    id = 120502
    type: SkillType = SkillType.ELEMENTAL_SKILL
    damage_type: SkillType = SkillType.ELEMENTAL_SKILL
    main_damage_element: ElementType = ElementType.HYDRO
    main_damage: int = 0
    piercing_damage: int = 0
    cost = [{'cost_num':3, 'cost_type':CostType.HYDRO}]
    energy_cost: int = 0
    energy_gain: int = 1

    def on_call(self, game: 'GeniusGame'):
        super().on_call(game)
        self.from_character.elemental_attach(game, ElementType.HYDRO)
        self.generate_summon(game, Bake_Kurage)
        self.gain_energy(game)
        game.manager.invoke(EventType.AFTER_USE_SKILL, game)


class Nereids_Ascension(ElementalBurst):
    name = "Nereid's Ascension"
    name_ch = "海人化羽"
    id = 120503
    type: SkillType = SkillType.ELEMENTAL_BURST
    damage_type: SkillType = SkillType.ELEMENTAL_BURST
    main_damage_element: ElementType = ElementType.HYDRO
    main_damage: int = 2
    piercing_damage: int = 0
    cost = [{'cost_num':3, 'cost_type':CostType.HYDRO}]
    energy_cost: int = 2
    energy_gain: int = 0

    def on_call(self, game: 'GeniusGame'):
        super().on_call(game)
        self.consume_energy(game)
        self.resolve_damage(game)
        for character in self.from_character.from_player.character_list:
            if character.is_alive:
                character.heal(heal=1, game=game)
        self.add_status(game, Ceremonial_Garment)
        if self.from_character.talent:
            summon = self.from_character.from_player.summon_zone.has_entity(Bake_Kurage)
            if summon is not None:
                summon.update()
        game.manager.invoke(EventType.AFTER_USE_SKILL, game)


class Bake_Kurage(Summon):
    name = 'Bake-Kurage'
    name_ch = '化海月'
    element = ElementType.HYDRO
    removable = True
    def __init__(self, game: 'GeniusGame', from_player: 'GeniusPlayer', from_character=None):
        super().__init__(game, from_player, from_character)
        self.usage: int = 2
        self.current_usage: int = 2
    def end_phase(self, game:'GeniusGame'):
        if game.active_player == self.from_player:
            dmg = Damage.create_damage(
                game,
                SkillType.SUMMON,
                self.element,
                1,
                0,
                self,
                get_opponent_active_character(game)
            )
            game.add_damage(dmg)
            game.resolve_damage()
            char = get_my_active_character(game)
            char.heal(1, game)
            self.current_usage -= 1
            if(self.current_usage <= 0):
                self.on_destroy(game)
    def update_listener_list(self):
        self.listeners = [
            (EventType.END_PHASE, ZoneType.SUMMON_ZONE, self.end_phase)
        ]

class Ceremonial_Garment(Status):
    name = 'Ceremonial Garment'
    name_ch = '仪来羽衣'
    def __init__(self, game: 'GeniusGame', from_player: 'GeniusPlayer', from_character=None):
        super().__init__(game, from_player, from_character)
        self.usage: int = 2
        self.current_usage: int = 2
    def after_skill(self, game:'GeniusGame'):
        if game.current_skill.from_character == self.from_character:
            if game.current_skill.type == SkillType.NORMAL_ATTACK:
                for character in self.from_character.from_player.character_list:
                    if character.is_alive:
                        character.heal(heal=1, game=game)
    def on_add_dmg(self, game:'GeniusGame'):
        if game.current_damage.damage_from == self.from_character:
            if game.current_damage.damage_type == SkillType.NORMAL_ATTACK:
                game.current_damage.main_damage += 1
        if self.from_character.talent and isinstance(game.current_damage.damage_from, Bake_Kurage):
            game.current_damage.main_damage += 1
    def on_begin(self, game:'GeniusGame'):
        self.current_usage -= 1
        if self.current_usage<=0:
            self.on_destroy(game)
    def update_listener_list(self):
        self.listeners = [
            (EventType.DAMAGE_ADD, ZoneType.CHARACTER_ZONE, self.on_add_dmg),
            (EventType.AFTER_USE_SKILL, ZoneType.CHARACTER_ZONE, self.after_skill),
            (EventType.BEGIN_ACTION_PHASE, ZoneType.CHARACTER_ZONE, self.on_begin)
        ]
class SangonomiyaKokomi(Character):
    id: int = 1205
    name: str = "Sangonomiya Kokomi"
    name_ch = "珊瑚宫心海"
    element: ElementType = ElementType.HYDRO
    weapon_type: WeaponType = WeaponType.CATALYST
    country: CountryType = CountryType.INAZUMA
    init_health_point: int = 10
    max_health_point: int = 10
    skill_list: List = [The_Shape_of_Water, Kurages_Oath, Nereids_Ascension]
    max_power: int = 2

    def __init__(self, game: 'GeniusGame', zone: 'CharacterZone', from_player: 'GeniusPlayer', index: int, from_character=None, talent=False):
        super().__init__(game, zone, from_player, index, from_character)
        self.power = 0
        self.talent = talent
        self.talent_skill = self.skills[2]