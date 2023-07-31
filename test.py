from voyager import Voyager

# You can also use mc_port instead of azure_login, but azure_login is highly recommended
azure_login = {
    "client_id": "d69be8dc-9a59-4f96-acd7-557b07330a65",
    "redirect_url": "https://127.0.0.1/auth-response",
    'secret_value': 'GI18Q~3GIFumHRkk-S~uQo2bQ6vtgM6PUqiRjatZ',
    "version": "1.19", # the version Voyager is tested on
}
openai_api_key = "YOUR_API_KEY"

voyager = Voyager(
    azure_login=azure_login,
    openai_api_key=openai_api_key,
)

# start lifelong learning
voyager.learn()