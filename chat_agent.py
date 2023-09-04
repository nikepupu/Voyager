
import openai
import time
import os
import sys
from MultiVoyager import MultiVoyager
from whisper_mic.whisper_mic import WhisperMic
import queue
import threading


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
    openai.api_key = 

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

env = MultiVoyager(33253, 'sk-x')

asset_file = './multi_voyager/prompt/prompt_human.txt'
example = open(asset_file, 'r').read().split('***\n')
example_history = []
message = """ You helping humans to play minecraft.
 Please follow human instructions. 
 When there is no instruction, please do not do anything."""

example_history.append(("system", message))
for idx, exp in enumerate(example):
    if idx % 2 == 0:
        example_history.append(("user", exp))
    else:
        example_history.append(("assistant", exp))

interaction_history = []


audio_queue = queue.Queue()
mic = WhisperMic()
def listen():
    while True:
        result = mic.listen(2)
        print('result: ', result)
        audio_queue.put_nowait(result)
x = threading.Thread(target=listen, daemon=True).start()

while True:
    # get everything from the audio queue
    human_instructiosn = []
    while not audio_queue.empty():
        human_instructiosn.append(audio_queue.get(False))
    
    total_instr = ""
    for instr in human_instructiosn:
        total_instr += instr + " "
    
    env.set_human_action(total_instr)
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

    

    
    

