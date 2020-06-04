from urnai.agents.actions import sc2 as scaux
from .collectables import CollectablesDeepRTSActionWrapper, CollectablesStarcraftIIActionWrapper
from pysc2.lib import actions, features, units
from statistics import mean
from pysc2.env import sc2_env
import math

class FindAndDefeatDeepRTSActionWrapper(CollectablesDeepRTSActionWrapper):
    def __init__(self):
        self.move_number = 0

        moveleft = 2
        moveright = 3
        moveup = 4
        movedown = 5
        attack = 10

        self.actions = [moveleft, moveright, moveup, movedown, attack] 


class FindAndDefeatStarcraftIIActionWrapper(CollectablesStarcraftIIActionWrapper):
    def __init__(self):
        super().__init__()
        self.maximum_attack_range = 3
        self.attack = 4
        self.actions = [self.moveleft, self.moveright, self.moveup, self.movedown, self.attack] 

    def solve_action(self, action_idx, obs):
        if action_idx == self.moveleft:
            self.move_left(obs)
        elif action_idx == self.moveright:
            self.move_right(obs)
        elif action_idx == self.moveup:
            self.move_up(obs)
        elif action_idx == self.movedown:
            self.move_down(obs)
        elif action_idx == self.attack:
            self.attack_(obs)
    
    def get_nearest_enemy_unit_inside_radius(self, x, y, obs, radius):
        enemy_army = [unit for unit in obs.raw_units if unit.owner != 1] 

        closest_dist = 9999999999999 
        closest_unit = None
        for unit in enemy_army:
            xaux = unit.x
            yaux = unit.y

            dist = abs(math.hypot(x - xaux, y - yaux))

            if dist <= closest_dist and dist <= radius:
                closest_dist = dist
                closest_unit = unit

        if closest_unit is not None:
            return closest_unit

    def attack_nearest_inside_radius(self, obs, radius):
        #get army coordinates
        army = scaux.select_army(obs, sc2_env.Race.terran)
        xs = [unit.x for unit in army]
        ys = [unit.y for unit in army]
        army_x = int(mean(xs))
        army_y = int(mean(ys))

        #get nearest unit
        enemy_unit = self.get_nearest_enemy_unit_inside_radius(army_x, army_y, obs, radius)

        #tell each unit in army to attack nearest enemy
        if enemy_unit is not None:
            for unit in army:
                self.pending_actions.append(actions.RAW_FUNCTIONS.Attack_pt("now", unit.tag, [enemy_unit.x, enemy_unit.y]))

    def attack_(self, obs):
        self.attack_nearest_inside_radius(obs, self.maximum_attack_range)
