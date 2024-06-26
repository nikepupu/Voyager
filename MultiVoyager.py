from voyager import Voyager
from typing import List
import time
import random
import time

from collections import Counter

import os


class MultiVoyager():
    def __init__(self, mc_port, openai_api_key, username='nikepupu9') -> None:
        self.mc_port = mc_port
        self.username = username
        self.agents = []
        self.time_step = 0
        openai_api_key = openai_api_key
    
        self.env = Voyager(
            mc_port=self.mc_port,
            openai_api_key=openai_api_key,
            server_port=3000,
            env_wait_ticks=20,
        )
        
        
        self.env.start()
        print('started ')
        code = """ 
                await bot1.chat('/gamerule doMobSpawning false');
                await bot1.chat('/tp @s -235 32 -109');
                await bot2.chat('/tp @s -229 32 -108');
                await bot3.chat('/tp @s -217 32 -53');
                await bot1.chat('/kill @e[type=!player]');
                await bot1.chat('/kill @e[type=item]');  
        """
        

        self.chestx = -217
        self.chesty = 32
        self.chestz = -51

        code += """
                await bot1.chat('/setblock -236 32 -103 minecraft:furnace');
                await bot1.chat('/setblock -230 33 -114 minecraft:chest');
                await bot1.chat('/setblock -217 32 -51 minecraft:chest');
                await bot1.chat('/setblock -226 39 -119 minecraft:air');
            """
        # this is used inside promise.call, cannot have ; 
        # self.copy_inventory_code = "updatePlayerChestInventory(bot3, -217, 32, -51)"
        # code += "await updatePlayerChestInventory(bot3, -217, 32, -51);"
        # code += f"await bot1.chat('/experience set {self.username} 0 levels');"
        self._last_event = self.env.step_manuual(code = code)

        print('first step done')
        self._last_event = self.env.step_manuual(code = "await updateEntities(bot1, '2');") 
                            
        self.feedback = ""

        self.task_list = ['cooked_chicken', 'cooked_mutton']

        self.rng = random.Random(123)
        self.task_interval = 10
        self.task_lifetime = int(self.task_interval * 1.5)
        self.goals = [(self.rng.choice(self.task_list), self.task_lifetime)]
        self.accomplished_goals = []
        self.failed_goals = []

        self.last_actions = []

        

    def all_state(self):
        
        # print(self._last_event)
        prompt = 'current dishes:   \n'
        for goal in self.goals:
            prompt += f"{goal[0]}: remaning time: {goal[1]} \n"
        

        prompt += f"Environment Feedback : {self.feedback} \n"
        prompt += f"t = {self.time_step} \n\n"
        for i in range(2):
            prompt += f"agent {i+1} inventory :\n"
            prompt += str(self._last_event[f'bot{i+1}'][-1][1]["inventory"])
            prompt += "\n"
            prompt += f"agent {i+1} sourrending :\n"
            voxels = [item for item in self._last_event[f'bot{i+1}'][-1][1]["voxels"] if isinstance(item, list)]
            prompt += str(voxels)
            prompt += "\n"
            prompt += f"agent {i+1} sourrending entities :\n"
            prompt += str(self._last_event[f'bot{i+1}'][-1][1]['status']["entities"])
            prompt += "\n"

        # prompt += f"player inventory :\n"
        # for key, value in self._last_event['bot3'][-1][1]["nearbyChests"].items():
        #     prompt += f" {value}"

        prompt += '\n'
        prompt += f"kitchen state :\n"
        prompt += 'Inside furnace : \n'

        for key, value in self._last_event[f'bot2'][-1][1]["nearbyFurnaces"].items():
            prompt += f" {value}"
        prompt += '\n'
        
        prompt += 'Inside chest : \n'
        for key, value in self._last_event[f'bot2'][-1][1]["nearbyChests"].items():
            prompt += f" {value}"
        prompt += '\n'
        prompt += f'Agent Actions: \n'
        return prompt
    
    

    def step(self, actions):
            
        if ( int(self.time_step)  % self.task_interval) == 0 and int(self.time_step) != 0:
            self.goals.append((self.rng.choice(self.task_list), self.task_lifetime))
        
        def extract_function_names(calls):
            import re
            function_names = []
            for call in calls:
                match = re.match(r"(\w+)\(", call)
                if match:
                    function_names.append(match.group(1))
            return function_names
        
        function_names = extract_function_names(actions)
        valid = True
        self.feedback = ""
        for function_name in function_names:
            if function_name not in ['goto', 'mineBlock', 'killMob', 'putItemFurnace', 'putFuelFurnace', 'takeOutFurnace', 'putInChest']:
                valid = False
                self.feedback += f'Function {function_name} is not supported. '


        
        def construct_action_str(actions):
            actions = actions + ["updateEntities(bot1, '2' )"]
            action_str = ""
            for i in range(len(actions)):
                action_str += f"{actions[i]},"
            action_str = action_str[:-1]
            return action_str
        action_str = construct_action_str(actions)
        if action_str == self.last_actions:
            self.feedback += 'You have already done this action last time, please do something else.'

        self.last_actions = action_str
        if valid:
            self._last_event = self.env.step_manuual(code = f"""
                                                        await Promise.all([{action_str}]);
                                                 """)
        self.time_step += 1
        
        for event in self._last_event['bot1']:
            if event[0] == 'onChat':
                message = ' For bot1 ' +   event[1]['onChat']
                self.feedback += message
        
        for event in self._last_event['bot2']:
            if event[0] == 'onChat':
                message = ' For bot2 ' +   event[1]['onChat']
                self.feedback += message
        

        # assuming one chest
        for key, value in self._last_event['bot2'][-1][1]["nearbyChests"].items():
            chest = value
            break
        
        # print('inside chest: ', chest)

        # Sort the goals based on time
        self.goals.sort(key=lambda x: x[1])
        # print('goals: ', self.goals)
        remaining_goals = self.goals.copy()  # Create a copy to iterate over

        for goal in remaining_goals:
            item, _ = goal
            if item in chest:
                accomplished_counter = Counter(self.accomplished_goals)
                if accomplished_counter[item] < chest[item]:
                    self.accomplished_goals.append(item)
                    self.goals.remove(goal)

        self.goals = [(goal[0], goal[1]-1) for goal in self.goals]
        expired_goals = [goal[0] for goal in self.goals if goal[1] == 0]
        self.failed_goals += expired_goals
        self.goals = [goal for goal in self.goals if goal[1] > 0]

        # print('accomplished goals: ', self.accomplished_goals)
        
        return self.all_state()


if __name__ == '__main__':
    
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    env = MultiVoyager(36677, openai_api_key)

    
    def case1():
        state = env.all_state()
        print(state) 
        print('***')
        actions = ["goto(bot1, 'oak_log')", "goto(bot2, 'chicken')"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = ["mineBlock(bot1, 'oak_log')", "killMob(bot2, 'chicken')"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = ["goto(bot1, 'furnace')", "goto(bot2, 'furnace')"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = ["putFuelFurnace(bot1, 'oak_log')", "putItemFurnace(bot2, 'chicken')"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = ["takeOutFurnace(bot1)"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = ["goto(bot1, 'chest')"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = ["putInChest(bot1, 'cooked_chicken')"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = ["goto(bot1, 'oak_log')"]
        state = env.step(actions)
        print('***')

    def case3():
        state = env.all_state()
        time.sleep(20.0)
        actions = [ "goto(bot2, 'chicken')", "goto(bot1, 'sheep')"]
        env.set_human_action("Let's cook chicken. I will get the oak_log")
        state = env.step(actions)
        
        actions = [ "killMob(bot2, 'chicken')", "killMob(bot1, 'sheep')"]
        env.set_human_action("")
        state = env.step(actions)
        time.sleep(2.0)
        
        actions = [ "goto(bot2, 'furnace')", ""]
        env.set_human_action("")
        state = env.step(actions)
        

        actions = [ "putItemFurnace(bot2, 'chicken')"]
        env.set_human_action("")
        state = env.step(actions)
        
        actions = ["goto(bot1, 'furnace')", "goto(bot2, 'sheep')"]
        env.set_human_action("I will take the chicken to chest.")
        state = env.step(actions)
        
        actions = ["putItemFurnace(bot1, 'mutton')"]
        env.set_human_action("")
        state = env.step(actions)

        time.sleep(3.0)

        actions = ["takeOutFurnace(bot1)"]
        env.set_human_action("You can take the mutton to chest.")
        state = env.step(actions)
        
        actions = ["goto(bot1, 'chest')"]
        env.set_human_action("")
        state = env.step(actions)

        actions = ["putInChest(bot1, 'cooked_mutton')"]
        env.set_human_action("Ok great! Let's do another round of chicken and mutton, I will get the chicken this time.")
        state = env.step(actions)
        time.sleep(3.0)
        
        time.sleep(1)
        actions = [ "goto(bot2, 'sheep')", "goto(bot1, 'oak_log')"]
        env.set_human_action("")
        state = env.step(actions)
        
        actions = [ "killMob(bot2, 'sheep')", "mineBlock(bot1, 'oak_log')"]
        env.set_human_action("")
        state = env.step(actions)

        actions = [ "goto(bot2, 'furnace')", "goto(bot1, 'furnace')"]
        env.set_human_action("")
        state = env.step(actions)
        
        actions = [ "putItemFurnace(bot2, 'mutton')", "putFuelFurnace(bot1, 'oak_log')"]
        env.set_human_action("I'll take the mutton to the chest, can you get me some more wood for the grilled chicken.")
        state = env.step(actions)
        time.sleep(5.0)

        actions = [ "goto(bot1, 'oak_log')"]
        env.set_human_action("")
        state = env.step(actions)

        actions = [ "mineBlock(bot1, 'oak_log')"]
        env.set_human_action("")
        state = env.step(actions)

        actions = [ "goto(bot1, 'furnace')"]
        env.set_human_action("")
        state = env.step(actions)

        actions = [ "putFuelFurnace(bot1, 'oak_log')"]
        env.set_human_action("I'll also take the chicken to the chest, thanks for the help!")
        state = env.step(actions)



    def case2():
        state = env.all_state()
        print(state) 
        print('***')
        time.sleep(2.0)
        actions = [ "goto(bot2, 'chicken')"]
        env.set_human_action("Let's cook chicken. I will get the oak_log")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = [ "killMob(bot2, 'chicken')"]
        env.set_human_action("")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = [ "goto(bot2, 'furnace')"]
        env.set_human_action("")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = [ "putItemFurnace(bot2, 'chicken')"]
        env.set_human_action("")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = [""]
        env.set_human_action("I will take the chicken to chest.")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = [""]
        env.set_human_action("")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = [""]
        env.set_human_action("")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        time.sleep(5)
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')

    case1()