from voyager import Voyager
from typing import List
import time


class MultiVoyager():
    def __init__(self, mc_port, openai_api_key, username='nikepupu9') -> None:
        self.mc_port = mc_port
        self.username = username
        self.agents = []
        openai_api_key = "sk-xxx"
    
        self.env = Voyager(
            mc_port=self.mc_port,
            openai_api_key=openai_api_key,
            server_port=3000,
            env_wait_ticks=20,
        )
        self.env.start()
        #  await bot1.chat('/summon sheep -5 -60 -10 {NoAI:1, DeathLootTable:"minecraft:entities/sheep/mutton",DeathLootTableSeed:-12345}');
        #         await bot1.chat('/summon chicken -3 -60 -10 {NoAI:1, DeathLootTable:"minecraft:entities/chicken",DeathLootTableSeed:-1234}');
        code = """ 
                await bot1.chat('/tp @s -10 -60 -15');
                await bot2.chat('/tp @s -10 -60 10');
                await bot3.chat('/tp @s 78 -60 78');
                await bot1.chat('/fill -120 -60 -120 120 -60 120 minecraft:air');
                await bot1.chat('/kill @e[type=!player]');
                await bot1.chat('/kill @e[type=item]');
                await bot1.chat('/setblock 0 -60 0 minecraft:chest');
                await bot1.chat('/setblock 2 -60 4 minecraft:oak_log');
                await bot1.chat('/setblock 2 -60 -2 minecraft:furnace');
                await bot1.chat('/fill 20 -60 20 20 -60 20 minecraft:air');          
                await bot1.chat('/setblock 80 -60 80 minecraft:chest');    
        """
        self.copy_inventory_code = f"updatePlayerChestInventory(bot3)"
        code += f"await updatePlayerChestInventory(bot3);"
        self._last_event = self.env.step_manuual(code = code)
        self._last_event = self.env.step_manuual(code = "await updateEntities(bot1, '1');") 
        print(self._last_event)
                            
        self.feedback = []

    def all_state(self):
        prompt = ""
        for i in range(2):
            prompt += f"agent {i+1} inventory :\n"
            prompt += str(self._last_event[f'bot{i+1}'][-1][1]["inventory"])
            prompt += "\n"
            prompt += f"agent {i+1} sourrending :\n"
            prompt += str(self._last_event[f'bot{i+1}'][-1][1]["voxels"])
            prompt += "\n"
            prompt += f"agent {i+1} sourrending entities :\n"
            prompt += str(self._last_event[f'bot{i+1}'][-1][1]['status']["entities"])
            prompt += "\n"

        prompt += f"player inventory :\n"
        for key, value in self._last_event['bot3'][-1][1]["nearbyChests"].items():
            prompt += f" {value}"

        prompt += '\n'
        prompt += f"kitchen state :\n"
        prompt += 'Inside furnace : \n'

        for key, value in self._last_event[f'bot{i+1}'][-1][1]["nearbyFurnaces"].items():
            prompt += f" {value}"
        prompt += '\n'
        
        prompt += 'Inside chest : \n'
        for key, value in self._last_event[f'bot{i+1}'][-1][1]["nearbyChests"].items():
            prompt += f" {value}"
        prompt += '\n'

        return prompt
    
    def step(self, actions):
        
        def construct_action_str(actions):
            # actions = actions + [self.copy_inventory_code]
            action_str = ""
            for i in range(len(actions)):
                action_str += f"{actions[i]},"
            action_str = action_str[:-1]
            return action_str
        action_str = construct_action_str(actions)
        self._last_event = self.env.step_manuual(code = f"await Promise.all([{action_str}]);")
        self._last_event = self.env.step_manuual(code = "await updatePlayerChestInventory(bot3);")   
        self._last_event = self.env.step_manuual(code = "await updateEntities(bot1, 1);") 
        return self.all_state()
    
    
    def validate_n_parse(self, cmd_strs: List[str]):
        # validate
        # return True, predicate, args, ignored_actions
        
        predicates = []
        args = []
        for cmd_str in cmd_strs:
            action = cmd_str
            cmd_str = cmd_str.split('_')
            if len(cmd_str) < 2 or len(cmd_str) > 3:
                # print('not enough arguments')
                self.feedback.append(f'not enough arguments for action {action}')
                return False, None, None, None

            predicate = cmd_str[0]
            if predicate not in ['get', 'goto', 'put', 'noop']:
                self.feedback.append(f'{predicate} is not in the list of supported actions')
                return False, None, None, None

            agent = cmd_str[1]
            try:
                agent = int(agent.replace('agent', ''))
            except:
                self.feedback.append(f'agent id not found')
                return False, None, None, None

            if len(cmd_str) == 2:
                # noop
                taget = None
                arg = [agent]
            elif len(cmd_str) == 3:
                #goto_agent0_somelocation
                #get_agent0_somelocation
                #put_agnet0_somelocation
                #activate_agnet0_somelocation

                #TODO:
                # need to test if the object can be activated

                target = cmd_str[-1]

                arg = [agent, target]


            predicates.append(predicate)
            args.append(arg)

        # agents must be differnt
        agents = [arg[0] for arg in args]
        if len(agents) != len(set(agents)):
            # print("duplicate agents")
            self.feedback.append(f'agent ids cannot be the same')
            return False, None, None, None


        # make sure no conflict in actions
        # get only if
        valid_predicates = []
        valid_args = []

        # TODO(jxma): avialable_actions won't be used as filtering as now
        # actions of differnt agents will be execed sequentially, therefore some
        # actions may become valid once the previous action is execed.
        ignored_actions = [False for _ in range(len(predicates))]

        # ignored_actions = []
        # avail_actions = self.available_actions(return_struct=True)
        # for predicate, arg in zip(predicates, args):
        #     agnet_id = int(arg[0])
        #     if  arg in avail_actions[agnet_id][predicate]:
        #         # valid_predicates.append(predicate)
        #         # valid_args.append(arg)
        #         ignored_actions.append(False)
        #     else:
        #         ignored_actions.append(True)

        # Initialize a list to store tuples of (predicate, arg, ignored_action)
        actions = list(zip(predicates, args, ignored_actions))

        # Separate the sorted lists back into predicates, args, and ignored_actions
        predicates, args, ignored_actions = zip(*actions)

        # Convert the sorted lists to regular lists
        predicates = list(predicates)
        args = list(args)
        ignored_actions = list(ignored_actions)

        return True, predicates, args, ignored_actions

if __name__ == '__main__':
    env = MultiVoyager(33157, 'sk-x')
    state = env.all_state()
    print(state) 
    print('###')
    actions = ["goto(bot1, 'oak_log')", "goto(bot2, 'chicken')"]
    state = env.step(actions)
    print(actions)
    print('###')
    print(state)
    print('###')
    actions = ["mineBlock(bot1, 'oak_log')", "killMob(bot2, 'chicken')"]
    state = env.step(actions)
    print(actions)
    print('###')
    print(state)
    print('###')
    actions = ["goto(bot1, 'furnace')", "goto(bot2, 'furnace')"]
    state = env.step(actions)
    print(actions)
    print('###')
    print(state)
    print('###')
    actions = ["putFuelFurnace(bot1, 'oak_log')", "putItemFurnace(bot2, 'chicken')"]
    state = env.step(actions)
    print(actions)
    print('###')
    print(state)
    print('###')
    actions = ["takeOutFurnace(bot1)"]
    state = env.step(actions)
    print(actions)
    print('###')
    print(state)
    print('###')
    actions = ["goto(bot1, 'chest')"]
    state = env.step(actions)
    print(actions)
    print('###')
    print(state)
    print('###')
    actions = ["putInChest(bot1, 'cooked_chicken')"]
    state = env.step(actions)
    print(actions)
    print('###')
    print(state)
    print('###')