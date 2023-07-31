from voyager import Voyager

# You can also use mc_port instead of azure_login, but azure_login is highly recommended

openai_api_key = ""

voyager2 = Voyager(
    mc_port=45617,
    openai_api_key=openai_api_key,
    server_port=3001
)



voyager2.env.reset()
voyager2.env.step("")

while True:
    continue
# start lifelong learning
# voyager.learn()


