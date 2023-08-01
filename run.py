from voyager import Voyager

# You can also use mc_port instead of azure_login, but azure_login is highly recommended
# check command: /data get entity bot3000 Inventory
openai_api_key = ""
port = 40521
voyager1 = Voyager(
    mc_port=port,
    openai_api_key=openai_api_key,
    server_port=3000,
    env_wait_ticks=40,
)



voyager1.start(position={'x': 212, 'y': 70, 'z': 707})
# voyager1.env.unpause()
print('voyager1 started')
# voyager2 = Voyager(
#     mc_port=port,
#     openai_api_key=openai_api_key,
#     server_port=3001
# )

# voyager2.start(position={'x': -35, 'y': 72, 'z': 498})
# voyager2.env.unpause()
# print('voyager2 started')
# print(voyager1.last_events)
# print('=====')
# print(voyager2.last_events)
found = False
foundItem = None
while True:
    data = voyager1.env.step(code = """exploreUntil(bot, new Vec3(1, 0, 1), 10,
                             () => {
                                const oak_logs = bot.findBlocks({
                                matching: block => block.name === `oak_log`,
                                maxDistance: 32,
                                count: 2
                                });
                                return oak_logs.length >= 2 ? oak_logs : null;
                            });""", 
                         programs=voyager1.skill_manager.programs)
    print('data: ', data)
    print('voxels', data[0][1]['voxels'])
    
    for item in data[0][1]['voxels']:
        if 'oak_log' == item:
            found = True
            foundItem = item
            break
    if found:
        break

x = voyager1.last_events[-1][1]['status']['position']['x']
y = voyager1.last_events[-1][1]['status']['position']['y']
z = voyager1.last_events[-1][1]['status']['position']['z']

# data = voyager2.env.step(code = f"bot.chat('/tp @s {x+5} {y+3} {z+5}') ")
# print('tp result: ', data)
data = voyager1.env.step(code = """ 
    async function mineWoodLog(bot) {
    const woodLogNames = ["oak_log", "birch_log", "spruce_log", "jungle_log", "acacia_log", "dark_oak_log", "mangrove_log"];

    // Find a wood log block
    const woodLogBlock = await exploreUntil(bot, new Vec3(1, 0, 1), 60, () => {
        return bot.findBlock({
        matching: block => woodLogNames.includes(block.name),
        maxDistance: 32
        });
    });
    if (!woodLogBlock) {
        bot.chat("Could not find a wood log.");
        return;
    }

    // Mine the wood log block
    await mineBlock(bot, woodLogBlock.name, 1);
    bot.chat("Wood log mined.");
    }
                         
    await mineWoodLog(bot);

 """, 
                         programs=voyager1.skill_manager.programs)
# print(voyager1.last_events)
print('voyager 1 data', data)

# data = voyager2.env.step(code = f"await mineBlock(bot, '{foundItem}', 1);", 
#                          programs=voyager2.skill_manager.programs)
# print('voyager 2 data', data)
# /home/nikepupu/project_micorsoft/Voyager/run.py
print(voyager1.last_events)
# print(voyager2.last_events)
print('done')
while True:
    continue

