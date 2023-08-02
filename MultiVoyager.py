from voyager import Voyager
from typing import List
import time


class MultiVoyager():
    def __init__(self, mc_port, num_agents, openai_api_key, init_positions) -> None:
        self.mc_port = mc_port
        self.agents = []
        assert len(init_positions) == num_agents

        for i in range(num_agents):
            agent = Voyager(
                mc_port=mc_port,
                openai_api_key=openai_api_key,
                server_port=3000+i,
                env_wait_ticks=100,
                )
            self.agents.append(agent)
            agent.start()
            agent.step_manuual(code = f"await bot.chat('/tp @s {init_positions[i]['x']} {init_positions[i]['y']} {init_positions[i]['z']} '); "  )
            if i < num_agents - 1:
                agent.env.unpause()
        
        for i in range(num_agents):
            self.agents[i].env.set_server_state(server_paused=True)
        
        self.feedback = []

    def all_state(self):
        prompt = ""
        for i in range(len(self.agents)):
            prompt += f"agent {i} inventory :\n"
            prompt += str(self.agents[i].last_events[-1][1]["inventory"])
            prompt += "\n"
            prompt += f"agent {i} sourrending :\n"
            prompt += str(self.agents[i].last_events[-1][1]["voxels"])
    def step(self, actions):
        self.feedback = []
        valid , predicates, args, ignored_actions = self.validate_n_parse(actions)

        for predicate, arg, ignored_action in zip(predicates, args, ignored_actions):
            agent = arg[0]
            #self.agents[i].step_manuual(code = self.obtain_code(actions[i]))
        
        return self.all_state()
    
    def obtain_code(self, predicate, arg):
        """
        sample action:
            explore-agent0-oak_log
            noop-agent0
            goto-agent0-agent1
            mine-agent0-oak_log
        """

        if predicate == 'explore':
            code = """await exploreUntil(bot, new Vec3(1, 0, 1), 10,
                                () => {
                                    const items = bot.findBlocks({
                                    matching: block => block.name === `{item}`,
                                    maxDistance: 32,
                                    count: 1
                                    });
                                    return items.length >= 1 ? items : null;
                                });""".format(arg[1])
        elif predicate == 'noop':
            code = ""
        elif predicate == 'goto':
            code = """await bot.chat('/tp @s {botname}');""".format( "bot"+str( int(arg[1][-1])+3000) )
        elif predicate == 'mine':
            code = """ await mineBlock(bot, '{item}', 1); """.format(arg[1])
        
        return code
        
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
            if predicate not in ['explore', 'goto', 'mine', 'noop']:
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

