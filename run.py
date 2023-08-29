from voyager import Voyager

# You can also use mc_port instead of azure_login, but azure_login is highly recommended
# check command: /data get entity bot3000 Inventory
openai_api_key = "sk-xxx"
port = 40463
voyager1 = Voyager(
    mc_port=port,
    openai_api_key=openai_api_key,
    server_port=3000,
    env_wait_ticks=20,
)



voyager1.start()
data = voyager1.step_manuual(code = """ 
                             await bot.chat('/fill -40 -60 -40 40 -60 40 minecraft:air');
                             await bot.chat('/kill @e[type=!player,x=0,y=-60,z=0,dx=40,dy=40,dz=40]');
                             await bot.chat('/kill @e[type=item,x=0,y=-40,z=0,dx=40,dy=40,dz=40]');
                             await bot.chat('/tp @s 0 -60 0');
                             
                             await bot.chat('/setblock 2 -60 2 minecraft:oak_log');
                             await bot.chat('/setblock 2 -60 -2 minecraft:furnace');
                              """  )

# voyager1.env.unpause()

# data = voyager1.step_manuual(code = """ 
#     await killMob(bot, 'sheep', 300);
#  """)

# data = voyager1.step_manuual(code = """
#     await mineBlock(bot, 'oak_log', 1);
#  """)
# data = voyager1.step_manuual(code = """ 
#    await goto(bot, 'sheep');
# """)
                             
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
# while True:
#     continue

