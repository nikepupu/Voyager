from voyager import Voyager

# You can also use mc_port instead of azure_login, but azure_login is highly recommended

openai_api_key = ""

voyager1 = Voyager(
    mc_port=45617,
    openai_api_key=openai_api_key,
    server_port=3000
)



voyager1.start()
voyager1.env.unpause()

voyager2 = Voyager(
    mc_port=45617,
    openai_api_key=openai_api_key,
    server_port=3005
)



voyager2.start()

while True:
    continue
# start lifelong learning
# voyager.learn()


