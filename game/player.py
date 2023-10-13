from utils import *
from typing import List, TYPE_CHECKING
from .zone import CardZone, ActiveZone, SummonZone, SupportZone, DiceZone, CharacterZone, HandZone
import numpy as np

if TYPE_CHECKING:
    from game.game import GeniusGame
    from game.action import Action
    from card.action import ActionCard

class GeniusPlayer:
    def __init__(self, game: GeniusGame, deck) -> None:
        # 初始化牌库、起始5张手牌、骰子区
        self.card_zone = CardZone(game, self, deck['action_card']) # 牌库区
        self.hand_zone: HandZone = HandZone(game, self) # 手牌区
        self.hand_zone.add(self.card_zone.get_card(num=5))
        self.dice_zone: DiceZone(game, self)

        # 初始化角色状态区
        self.active_idx = -1
        self.character_list: List[CharacterZone] = []
        for name in deck['character']:
            self.character_list.append(CharacterZone(game, self, name))
        self.character_num = len(self.character_list)

        # 环境中的基本状态
        self.support_zone: SupportZone = SupportZone(game, self)
        self.summons_zone: SummonZone = SummonZone(game, self)
        self.team_combat_status: ActiveZone = ActiveZone(game, self)

        # 其他基本信息
        self.is_pass: bool
        self.is_after_change: bool
        self.is_quick_change: bool
        self.change_num: int
    
    def choose_card(self, action):
        '''
            非标准行动: 制衡手牌
        '''
        throw_card = []
        for idx in range(self.hand_zone.num()):
            if action[idx] == 0:
                throw_card.append(self.hand_zone.remove(idx))
        reget_card = self.card_zone.get_card(num=len(throw_card))
        self.card_zone.return_card(throw_card)
        self.hand_zone.add(reget_card)
        
    def choose_character(self, action):
        '''
            非标准行动: 选择出战角色
        '''
        idx = np.where(action==1)
        self.change_to_id(idx)
        

    def choose_dice(self, action):
        '''
            非标准行动: 选择重新投掷的骰子
        '''
        reroll_num = np.sum(action)
        reroll_dice = self.roll_dice(num=reroll_num)
        for idx in len(self.dice_zone):
            if action[idx] == 0:
                self.dice_zone.pop(idx)
        self.dice_zone += reroll_dice

    def roll_dice(self, num=8):
        '''
            基本行动: 投掷骰子
        '''
        return np.random.randint(0, DICENUM, num)
    
    def get_dice(self, dices):
        '''
            基本行动: 获取骰子
        ''' 
    
    def use_dice(self, dices):
        '''
            基本行动: 使用骰子
        ''' 

    def get_card(self, num):
        '''
            基本行动: 获取牌
        '''
        get_cards = self.card_zone.get_card(num=num)
        self.hand_zone.add(get_cards)
    
    def change_to_id(self, idx):
        '''
            基本行动: 切换到指定人
        '''
        if self.active_idx > 0:
            self.character_list[self.active_idx].is_active = False
        self.active_idx = idx
        self.character_list[self.active_idx].is_active = True
        self.is_after_change = True

    def change_to_previous_character(self):
        '''
            基本行动: 切换到前一个人
        '''
        idx = (self.active_idx - 1) % self.character_num
        while self.character_list[idx].is_alive == False:
            idx = (idx - 1) % self.character_num
        self.change_to_id(idx)
    
    def change_to_next_character(self):
        '''
            基本行动: 切换到下一个人
        '''
        idx = (self.active_idx + 1) % self.character_num
        while self.character_list[idx].is_alive == False:
            idx = (idx - 1) % self.character_num
        self.change_to_id(idx)

    def use_skill(self, game: 'GeniusGame'):
        '''
            标准行动: 使用技能
        '''
        ### TODO: 判断使用哪个技能
        skill = None
        ###
        self.character_list[self.active_idx].skill(skill, game)
        self.is_after_change = False
    
    def play_card(self, game: 'GeniusGame'):
        '''
            标准行动: 打出手牌
        '''
        ### TODO: 判断打出哪张手牌
        idx = None
        ###
        card: ActionCard = self.hand_zone.remove(idx)
        card.on_played(game)

    def change_character(self, game: 'GeniusGame'):
        '''
            标准行动: 切换角色
        '''
        ### TODO: 判断切换到哪个角色
        idx = None
        ###
        self.change_to_id(idx)
        
    
    def begin_round(self, Game):
        '''
            结算时刻: 回合开始时
        '''
        # 维护状态结算
        self.is_pass = False
        self.is_after_change = False
        self.is_quick_change = False
        self.change_num = 0

        # 事件

    def end_round(self, Game):
        '''
            结算时刻: 回合结束时
        '''
        # 事件

        # 摸牌
        self.get_card(num=2)





