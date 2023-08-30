from voyager import Voyager

# You can also use mc_port instead of azure_login, but azure_login is highly recommended
# check command: /data get entity bot3000 Inventory
openai_api_key = "sk-xxx"
port = 44401
voyager1 = Voyager(
    mc_port=port,
    openai_api_key=openai_api_key,
    server_port=3000,
    env_wait_ticks=20,
)

voyager1.start()
#  await bot1.chat('/tp @s 0 -60 0');
data = voyager1.step_manuual(code = """ 
                             await bot1.chat('/tp @s -10 -60 -15');
                             await bot2.chat('/tp @s -10 -60 10');
                             await bot1.chat('/fill -40 -60 -40 40 -60 40 minecraft:air');
                             await bot1.chat('/kill @e[type=!player]');
                             await bot1.chat('/kill @e[type=item]');
                             await bot1.chat('/summon sheep -5 -60 -10 {NoAI:1, DeathLootTable:"minecraft:entities/sheep/mutton",DeathLootTableSeed:-12345}');
                             await bot1.chat('/summon chicken -3 -60 -10 {NoAI:1, DeathLootTable:"minecraft:entities/chicken",DeathLootTableSeed:-1234}');
                             await bot1.chat('/setblock 0 -60 0 minecraft:chest');
                             await bot1.chat('/setblock 2 -60 4 minecraft:oak_log');
                             await bot1.chat('/setblock 2 -60 -2 minecraft:furnace');
                              """  )

# voyager1.env.unpause()

# data = voyager1.step_manuual(code = """ 
#     await killMob(bot, 'sheep', 300);
#  """)

# data = voyager1.step_manuual(code = """
#     await mineBlock(bot, 'oak_log', 1);
#  """)
print(data)
print()

data = voyager1.step_manuual(code = """ 
   await Promise.all([goto(bot1, 'oak_log'), goto(bot2, 'chicken')])            
""")
                             
data = voyager1.step_manuual(code = """ 
   await Promise.all([mineBlock(bot1, 'oak_log', 1), killMob(bot2, 'chicken', 300)])            
""")
                             
                        
data = voyager1.step_manuual(code = """ 
   await Promise.all([goto(bot1, 'furnace'), goto(bot2, 'furnace')])            
""")

data = voyager1.step_manuual(code = """ 
   await Promise.all([putFuelFurnance(bot1, 'oak_log'), putItemFurnance(bot2, 'chicken')])            
""")

data = voyager1.step_manuual(code = """ await Promise.all([ takeOutFurnance(bot1)])  """)  
 
data = voyager1.step_manuual(code = """ 
   await Promise.all([goto(bot1, 'chest')])            
""")

print(data)
print()
data = voyager1.step_manuual(code = """ await Promise.all([ putInChest(bot1, 'cooked_chicken')])  """)                     
# data = voyager1.step_manuual(code = """ 
#    await goto(bot, 'furnace');
# """)
# data = voyager1.step_manuual(code = """
#     await putItemFurnance(bot, 'mutton');
#  """)
# data = voyager1.step_manuual(code = "await putFuelFurnance(bot, 'oak_log');")

# data = voyager1.step_manuual(code = """ await takeOutFurnance(bot); """)
print(data)

voyager1.env.unpause()
# print('voyager1 started')
# voyager2 = Voyager(
#     mc_port=port,
#     openai_api_key=openai_api_key,
#     server_port=3001,
#     env_wait_ticks=40,
# )
# voyager2.start()
# voyager1.env.set_server_state(server_paused=True)

# data = voyager2.step_manuual(code = "await bot.chat('/tp @s 140 78 702'); "  )
# data = voyager2.step_manuual(code = "await bot.chat('/summon chicken 120 74 690'); "  )
# # voyager2.start(position={'x': -35, 'y': 72, 'z': 498})
# # voyager2.env.unpause()
# # print('voyager2 started')
# # print(voyager1.last_events)
# # print('=====')
# # print(voyager2.last_events)
# found = [False, False]
# while True:
#     if not found[0]:
#         data = voyager1.step_manuual(code =
#             """
#             const chicken = await exploreUntil(bot, new Vec3(1, 0, 1), 60, () => {
#             const chicken = bot.nearestEntity(entity => {
#                     return entity.name === "chicken" && entity.position.distanceTo(bot.entity.position) < 32;
#             });
#             if(chicken)
#                 bot.chat('chicken found bot1');
#             return chicken;

#             });""")
#         # print(data, 'bot1', data[0][1]['blockRecords'])
#         for item in data[0][1]['status']['entities']:
#             if 'chicken' == item:
#                 found[0] = True
#                 foundItem = item
#                 break
#     if not found[1]:
#         data = voyager2.step_manuual(code =
#             """
#             const chicken = await exploreUntil(bot, new Vec3(1, 0, -1), 60, () => {
#             const chicken = bot.nearestEntity(entity => {
#                     return entity.name === "chicken" && entity.position.distanceTo(bot.entity.position) < 32;
#             });
#             if(chicken)
#                 bot.chat('chicken found bot2');
#             return chicken;

#             });""")
#         # print(data, 'bot2', data[0][1]['blockRecords'])
#         for item in data[0][1]['status']['entities']:
#             if 'chicken' == item:
#                 found[1] = True
#                 break
#     if sum(found) == 2:
#         break
               
# # data = voyager2.env.step(code = f"bot.chat('/tp @s {x+5} {y+3} {z+5}') ")
# # print('tp result: ', data)
# # print(voyager1.last_events)
# print('voyager 1 data', data)
# data = voyager2.step_manuual(code = """ 
#     await killMob(bot, 'chicken', 300);
#  """)

# print(voyager1.last_events)
# # print(voyager2.last_events)
# print('done')
# print(voyager1.last_events[-1][1]["inventory"])
# print(voyager2.last_events[-1][1]["inventory"])

