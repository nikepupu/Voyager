
import openai
import time
from MultiVoyager import MultiVoyager
import threading
import pyautogui
import time
import azure.cognitiveservices.speech as speechsdk
from pynput.keyboard import Key, Controller
import pynput
import os

stop_recognition = threading.Event()
my_keyboard = Controller()

def type_in_chat(message):  
    pyautogui.press('t')
    pyautogui.press('backspace')
    pyautogui.write(message, interval=0.00)
    time.sleep(0.3)
    pyautogui.press('enter')
    time.sleep(0.1)
    pyautogui.press('esc')

def recognize_from_microphone():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_config.speech_recognition_language="en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    while not stop_recognition.is_set():
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(speech_recognition_result.text))
            type_in_chat(speech_recognition_result.text)
            env.set_human_action(speech_recognition_result.text)
            return speech_recognition_result.text
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

        return None
    
def on_press(key):
    global stop_recognition
    if key == Key.delete:
        stop_recognition.clear()
        recognize_from_microphone()
        stop_recognition.set()

def on_release(key):
    pass

def start_listener():
    with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
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

env = MultiVoyager(63605, 'sk-x')
listener_thread = threading.Thread(target=start_listener)
listener_thread.start()

asset_file = './multi_voyager/prompt/prompt_human.txt'
example = open(asset_file, 'r').read().split('***\n')
example_history = []
message = """ 
You are assisting humans in playing Minecraft. Always adhere to the following guidelines:

1. Prioritize following human instructions.
2. If there are no provided instructions, remain inactive.
3. If a human player expresses a desire to perform an action, do not intervene or take over. Allow the player to engage and enjoy the experience on their own.
"""

example_history.append(("system", message))
for idx, exp in enumerate(example):
    if idx % 2 == 0:
        example_history.append(("user", exp))
    else:
        example_history.append(("assistant", exp))

interaction_history = []

print('recording start')

while True:
        if env.human_actions_buffer or env.human_dialogs_history:
            env.buffer_human_action()
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