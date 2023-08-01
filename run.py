from voyager import Voyager

# You can also use mc_port instead of azure_login, but azure_login is highly recommended
# check command: /data get entity bot3000 Inventory
openai_api_key = ""
port = 40521
voyager1 = Voyager(
    mc_port=port,
    openai_api_key=openai_api_key,
    server_port=3000,
    env_wait_ticks=100,
)



voyager1.start()
data = voyager1.step_manuual(code = "await bot.chat('/tp @s 131 78 702'); "  )
voyager1.env.unpause()

print('voyager1 started')
voyager2 = Voyager(
    mc_port=port,
    openai_api_key=openai_api_key,
    server_port=3001
)
voyager2.start()
voyager1.env.set_server_state(server_paused=True)

data = voyager2.step_manuual(code = "await bot.chat('/tp @s 140 78 702'); "  )
# voyager2.start(position={'x': -35, 'y': 72, 'z': 498})
# voyager2.env.unpause()
# print('voyager2 started')
# print(voyager1.last_events)
# print('=====')
# print(voyager2.last_events)
found = [False, False]
while True:
    if not found[0]:
        data = voyager1.step_manuual(code =
                                    """await exploreUntil(bot, new Vec3(1, 0, 1), 10,
                                () => {
                                    const oak_logs = bot.findBlocks({
                                    matching: block => block.name === `oak_log`,
                                    maxDistance: 32,
                                    count: 1
                                    });
                                    return oak_logs.length >= 1 ? oak_logs : null;
                                });""")
        
        for item in data[0][1]['voxels']:
            if 'oak_log' == item:
                found[0] = True
                foundItem = item
                break
    if not found[1]:
        data = voyager2.step_manuual(code =
                                    """await exploreUntil(bot, new Vec3(1, 0, 1), 10,
                                () => {
                                    const oak_logs = bot.findBlocks({
                                    matching: block => block.name === `oak_log`,
                                    maxDistance: 32,
                                    count: 1
                                    });
                                    return oak_logs.length >= 1 ? oak_logs : null;
                                });""")
        
        for item in data[0][1]['voxels']:
            if 'oak_log' == item:
                found[1] = True
                break
    if sum(found) == 2:
        break
               
# data = voyager2.env.step(code = f"bot.chat('/tp @s {x+5} {y+3} {z+5}') ")
# print('tp result: ', data)
data = voyager1.step_manuual(code = """ 
                         
    await mineBlock(bot, 'oak_log', 1);

 """)
# print(voyager1.last_events)
print('voyager 1 data', data)
data = voyager2.step_manuual(code = """ 
    await mineBlock(bot, 'oak_log', 1);
 """)

print(voyager1.last_events)
# print(voyager2.last_events)
print('done')
print(voyager1.last_events[-1][1]["inventory"])
print(voyager2.last_events[-1][1]["inventory"])
while True:
    continue

