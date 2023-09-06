
import openai
import time
import os
import sys
from MultiVoyager import MultiVoyager
import queue
import threading
import pyautogui
from whisper_mic.whisper_mic import WhisperMic
key_id = 0

def chat_llm(history, temperature=0, max_tokens=100, model='gpt-4', context=''):
    # history = [('user', context)] + history    

    chat_history = []
    for i in history:
        if i[0] == 'user':
            chat_history.append({
                'role': 'user',
                'content': i[1]
            })
        elif i[0] == 'assistant':
            chat_history.append({
                'role': 'assistant',
                'content': i[1]
            })
        elif i[0] == 'system':
            chat_history.append({
                'role': 'system',
                'content': i[1]
            })
        else:
            raise NotImplementedError
    # openai.organization = 'org-m2iXhDFphTS3ttoq3L6gNNA0'

    total_trials = 0
    while True:

        try:
            response = openai.ChatCompletion.create(
                model = model,
                messages=chat_history,
                temperature=temperature,
                max_tokens=max_tokens
            )
            break
        except openai.OpenAIError as e:
            # print(e)
            
            total_trials += 1
            time.sleep(0.1)
    return response.choices[0].message.content

def next_key():
    global key_id
    with open('./key.txt', 'r') as f:
        all_keys = f.read().split('\n')
    # all_keys = open('./key.txt', 'r').read().split('\n')
    num = len(all_keys)
    key_id += 1

    if key_id >= num:
        key_id -= num

    openai.api_key = all_keys[key_id%num] #random.choice(all_keys)

env = MultiVoyager(39357, 'sk-x')

asset_file = './multi_voyager/prompt/prompt.txt'
example = open(asset_file, 'r').read().split('***\n')
example_history = []
message = """ 
You are allocating two agents to playing a cooking game in Minecraft. Always adhere to the following guidelines:

1. Prioritize current dishes.
2. Prioritize efficiency.
"""

example_history.append(("system", message))
for idx, exp in enumerate(example):
    if idx % 2 == 0:
        example_history.append(("user", exp))
    else:
        example_history.append(("assistant", exp))

interaction_history = []


for _ in range(60):
    prompt = env.all_state()
    interaction_history.append(("user", prompt))

    if len(interaction_history) > 5:
        interaction_history = interaction_history[2:]
    print(prompt)
    full_prompt = example_history + interaction_history
    plan = chat_llm(full_prompt, temperature=0.0, max_tokens=100, model='gpt-4', context='')
    print(plan)
    example_history.append(("assistant", plan))
    
    interaction_history.append(("assistant", plan))
    plan = eval(plan)
    env.step(plan)
    print('accomplished tasks: ', env.accomplished_goals)
    print('failed tasks: ', env.failed_goals)