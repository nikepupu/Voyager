from voyager import Voyager

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

    def all_state(self):
        prompt = ""
        for i in range(len(self.agents)):
            prompt += f"agent {i} inventory :\n"
            prompt += str(self.agents[i].last_events[-1][1]["inventory"])
            prompt += "\n"
            prompt += f"agent {i} sourrending :\n"
            prompt += str(self.agents[i].last_events[-1][1]["voxels"])
    def step(self, actions):

        for i in range(len(self.agents)):
            self.agents[i].step_manuual(code = self.obtain_code(actions[i]))
        
        return self.all_state()
    
    def obtain_code(self, action):
        """
        sample action:
            agent0-explore
            agent0-goto-agent1
            agent0-mine-oak_log
        """
        return None

