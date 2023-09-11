from voyager import Voyager
from typing import List
import time
import random
import time
import pyautogui
import threading
import queue
import threading
import time
import os
import azure.cognitiveservices.speech as speechsdk
from pynput.keyboard import Key, Controller
import pynput

stop_recognition = threading.Event()
my_keyboard = Controller()

# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
speech_config.speech_recognition_language="en-US"

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

def recognize_from_microphone():
        print("Speak into your microphone.")
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(speech_recognition_result.text))
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

class MultiVoyager():
    def __init__(self, mc_port, openai_api_key, username='nikepupu9') -> None:
        self.mc_port = mc_port
        self.username = username
        self.agents = []
        self.time_step = 0
        openai_api_key = "sk-xxx"
    
        self.env = Voyager(
            mc_port=self.mc_port,
            openai_api_key=openai_api_key,
            server_port=3000,
            env_wait_ticks=20,
        )
        
        self.env.start()
        # await bot1.chat('/summon sheep -5 -60 -10 {NoAI:1, DeathLootTable:"minecraft:entities/sheep/mutton",DeathLootTableSeed:-12345}');
        # await bot1.chat('/summon chicken -3 -60 -10 {NoAI:1, DeathLootTable:"minecraft:entities/chicken",DeathLootTableSeed:-1234}');
        code = """ 
                await bot1.chat('/gamerule doMobSpawning false');
                await bot1.chat('/tp @s -235 32 -109');
                await bot2.chat('/tp @s -229 32 -108');
                await bot3.chat('/tp @s -217 32 -53');
                await bot1.chat('/kill @e[type=!player]');
                await bot1.chat('/kill @e[type=item]');  
        """
        # await bot1.chat('/setblock 2 -60 -2 minecraft:furnace');
        # await bot1.chat('/setblock 0 -60 0 minecraft:chest');
        # await bot1.chat('/setblock 2 -60 4 minecraft:oak_log');
        # await bot1.chat('/fill 20 -60 20 20 -60 20 minecraft:air');  

        self.chestx = -217
        self.chesty = 32
        self.chestz = -51

        code += """
                await bot1.chat('/setblock -236 32 -103 minecraft:furnace');
                await bot1.chat('/setblock -230 33 -114 minecraft:chest');
                await bot1.chat('/setblock -217 32 -51 minecraft:chest');
                await bot1.chat('/setblock -226 39 -119 minecraft:air');
            """
        # this is used inside promise.call, cannot have ; 
        self.copy_inventory_code = "updatePlayerChestInventory(bot3, -217, 32, -51)"
        # code += "await updatePlayerChestInventory(bot3, -217, 32, -51);"
        # code += f"await bot1.chat('/experience set {self.username} 0 levels');"
        self._last_event = self.env.step_manuual(code = code)

        print('first step done')
        self._last_event = self.env.step_manuual(code = "await updateEntities(bot1, '2');") 
                            
        self.feedback = ""
        self.human_dialogs_history = ""

        self.task_list = ['cooked_chicken', 'cooked_mutton']

        self.rng = random.Random(1234)
        self.goals = [(self.rng.choice(self.task_list), 12)]
        self.accomplished_goals = []
        self.failed_goals = []

        self.last_actions = []

        self.goal = ''

        self.human_actions_buffer = ""

        

    def goal_checking_prompt(self):
        prompt = "Player Action: {self.huamn_actions} \n"
        prompt += f"t = {self.time_step} \n"
        for i in range(2):
            prompt += f"agent {i+1} inventory :\n"
            prompt += str(self._last_event[f'bot{i+1}'][-1][1]["inventory"])
            prompt += "\n"
            prompt += f"agent {i+1} surrounding :\n"
            voxels = [item for item in self._last_event[f'bot{i+1}'][-1][1]["voxels"] if isinstance(item, list)]
            
            prompt += voxels
            prompt += "\n"
            prompt += f"agent {i+1} surrounding entities :\n"
            prompt += str(self._last_event[f'bot{i+1}'][-1][1]['status']["entities"])
            prompt += "\n"

        prompt += f"player inventory :\n"
        for key, value in self._last_event['bot3'][-1][1]["nearbyChests"].items():
            prompt += f" {value}"

        prompt += '\n'
        prompt += f"kitchen state :\n"
        prompt += 'Inside furnace : \n'

        for key, value in self._last_event[f'bot{i+1}'][-1][1]["nearbyFurnaces"].items():
            prompt += f" {value}"
        prompt += '\n'
        
        prompt += 'Inside chest : \n'
        for key, value in self._last_event[f'bot{i+1}'][-1][1]["nearbyChests"].items():
            prompt += f" {value}"
        prompt += '\n'
        prompt += """ Did the player finish the action '{self.human_actions}' ? \n
        Pay attention to player inventory. Answer yes or no. Do not include reasoning. \n"""
        return prompt

    def all_state(self):
        
        # print(self._last_event)
        # prompt = 'current dishes:   \n'
        # for goal in self.goals:
        #     prompt += f"{goal[0]}: remaning time: {goal[1]} \n"
        
        # for goal in self.goals:
        #     prompt += f"{goal[0]} \n"

        prompt = f"Human Current Instruction: {self.goal} \n"
        prompt += f"Environment Feedback : {self.feedback} \n"
        prompt += f"t = {self.time_step} \n\n"
        for i in range(2):
            prompt += f"agent {i+1} inventory :\n"
            prompt += str(self._last_event[f'bot{i+1}'][-1][1]["inventory"])
            prompt += "\n"
            prompt += f"agent {i+1} surrounding :\n"
            voxels = [item for item in self._last_event[f'bot{i+1}'][-1][1]["voxels"] if isinstance(item, list)]
            prompt += str(voxels)
            prompt += "\n"
            prompt += f"agent {i+1} surrounding entities :\n"
            prompt += str(self._last_event[f'bot{i+1}'][-1][1]['status']["entities"])
            prompt += "\n"

        prompt += f"player inventory :\n"
        for key, value in self._last_event['bot3'][-1][1]["nearbyChests"].items():
            prompt += f" {value}"

        prompt += '\n'
        prompt += f"kitchen state :\n"
        prompt += 'Inside furnace : \n'

        for key, value in self._last_event[f'bot{i+1}'][-1][1]["nearbyFurnaces"].items():
            prompt += f" {value}"
        prompt += '\n'
        
        prompt += 'Inside chest : \n'
        for key, value in self._last_event[f'bot{i+1}'][-1][1]["nearbyChests"].items():
            prompt += f" {value}"

        prompt += '\n'
        prompt += f'Human Instructions Hisotry : {self.human_dialogs_history}\n'
        prompt += f'Agent Actions: \n'
        return prompt
    
    def set_human_action(self, human_actions = ""):
        self.human_actions_buffer +=  human_actions
        
    
    def clear_human_action(self):
        self.human_actions = ""

    def buffer_human_action(self):
        # put buffer into history
        if self.human_actions_buffer:
            self.human_dialogs_history += self.human_actions_buffer
            self.goal = self.human_actions_buffer
            self.human_actions_buffer = ""

    def step(self, actions):
            
        self.buffer_human_action()

        self.feedback = ""
        def construct_action_str(actions):
            actions = actions + [self.copy_inventory_code,  "updateEntities(bot1, '2' )"]
            action_str = ""
            for i in range(len(actions)):
                action_str += f"{actions[i]},"
            action_str = action_str[:-1]
            return action_str
        action_str = construct_action_str(actions)
        if action_str == self.last_actions:
            self.feedback= 'You have already done this action last time, please do something else.'

        self.last_actions = action_str
        self._last_event = self.env.step_manuual(code = f"""
                                                    await Promise.all([{action_str}]);
                                                 """)
        self.time_step += 1
        
        for event in self._last_event['bot1']:
            if event[0] == 'onChat':
                message = ' For bot1 ' +   event[1]['onChat']
                self.feedback += message
        
        for event in self._last_event['bot2']:
            if event[0] == 'onChat':
                message = ' For bot2 ' +   event[1]['onChat']
                self.feedback += message
        # inventory = self._last_event[f'bot1'][-1][1]["inventory"]
        # for goal in self.goals:
        #     if goal[0] in inventory:
        #         accomplished_counter = Counter(self.accomplished_goals)
        #         inventory_counter = Counter(inventory)
        #         if accomplished_counter[goal] < inventory_counter[goal]:

        #             self.accomplished_goals.append(goal)
        #         self.goals.remove(goal)

        # self.goals = [(goal[0], goal[1]-1) for goal in self.goals]
        # expired_goals = [goal for goal in self.goals if goal[1] == 0]
        # self.failed_goals += expired_goals
        # self.goals = [goal for goal in self.goals if goal[1] > 0]

        # print(self._last_event)
        
        return self.all_state()
    
def type_in_chat(message):  
    pyautogui.press('t')
    pyautogui.press('backspace')
    pyautogui.write(message, interval=0.00)
    time.sleep(0.2)
    pyautogui.press('enter')

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

def on_release(key):
    global stop_recognition
    if key == Key.delete:
        stop_recognition.set()


def start_listener():
    with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == '__main__':
    

    env = MultiVoyager(54230, 'sk-x')

    # Start the listener in a separate thread
    listener_thread = threading.Thread(target=start_listener)
    listener_thread.start()
    
    def case1():
        state = env.all_state()
        print(state) 
        print("Agent Actions: \n")
        print('***')
        actions = ["goto(bot1, 'oak_log')", "goto(bot2, 'chicken')"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print("Agent Actions: \n")
        print('***')
        actions = ["mineBlock(bot1, 'oak_log')", "killMob(bot2, 'chicken')"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print("Agent Actions: \n")
        print('***')
        actions = ["goto(bot1, 'furnace')", "goto(bot2, 'furnace')"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print("Agent Actions: \n")
        print('***')
        actions = ["putFuelFurnace(bot1, 'oak_log')", "putItemFurnace(bot2, 'chicken')"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print("Agent Actions: \n")
        print('***')
        actions = ["takeOutFurnace(bot1)"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print("Agent Actions: \n")
        print('***')
        actions = ["goto(bot1, 'chest')"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print("Agent Actions: \n")
        print('***')
        actions = ["putInChest(bot1, 'cooked_chicken')"]
        state = env.step(actions)
        print(actions)
        print('***')
        print(state)
        print('***')

    def case3():
        state = env.all_state()
        time.sleep(20.0)
        actions = [ "goto(bot2, 'chicken')", "goto(bot1, 'sheep')"]
        env.set_human_action("Let's cook chicken. I will get the oak_log")
        state = env.step(actions)
        
        actions = [ "killMob(bot2, 'chicken')", "killMob(bot1, 'sheep')"]
        env.set_human_action("")
        state = env.step(actions)
        time.sleep(2.0)
        
        actions = [ "goto(bot2, 'furnace')", ""]
        env.set_human_action("")
        state = env.step(actions)
        

        actions = [ "putItemFurnace(bot2, 'chicken')"]
        env.set_human_action("")
        state = env.step(actions)
        
        actions = ["goto(bot1, 'furnace')", "goto(bot2, 'sheep')"]
        env.set_human_action("I will take the chicken to chest.")
        state = env.step(actions)
        
        actions = ["putItemFurnace(bot1, 'mutton')"]
        env.set_human_action("")
        state = env.step(actions)

        time.sleep(3.0)

        actions = ["takeOutFurnace(bot1)"]
        env.set_human_action("You can take the mutton to chest.")
        state = env.step(actions)
        
        actions = ["goto(bot1, 'chest')"]
        env.set_human_action("")
        state = env.step(actions)

        actions = ["putInChest(bot1, 'cooked_mutton')"]
        env.set_human_action("Ok great! Let's do another round of chicken and mutton, I will get the chicken this time.")
        state = env.step(actions)
        time.sleep(3.0)
        
        time.sleep(1)
        actions = [ "goto(bot2, 'sheep')", "goto(bot1, 'oak_log')"]
        env.set_human_action("")
        state = env.step(actions)
        
        actions = [ "killMob(bot2, 'sheep')", "mineBlock(bot1, 'oak_log')"]
        env.set_human_action("")
        state = env.step(actions)

        actions = [ "goto(bot2, 'furnace')", "goto(bot1, 'furnace')"]
        env.set_human_action("")
        state = env.step(actions)
        
        actions = [ "putItemFurnace(bot2, 'mutton')", "putFuelFurnace(bot1, 'oak_log')"]
        env.set_human_action("I'll take the mutton to the chest, can you get me some more wood for the grilled chicken.")
        state = env.step(actions)
        time.sleep(5.0)

        actions = [ "goto(bot1, 'oak_log')"]
        env.set_human_action("")
        state = env.step(actions)

        actions = [ "mineBlock(bot1, 'oak_log')"]
        env.set_human_action("")
        state = env.step(actions)

        actions = [ "goto(bot1, 'furnace')"]
        env.set_human_action("")
        state = env.step(actions)

        actions = [ "putFuelFurnace(bot1, 'oak_log')"]
        env.set_human_action("I'll also take the chicken to the chest, thanks for the help!")
        state = env.step(actions)



    def case2():
        state = env.all_state()
        print(state) 
        print('***')
        time.sleep(2.0)
        actions = [ "goto(bot2, 'chicken')"]
        env.set_human_action("Let's cook chicken. I will get the oak_log")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = [ "killMob(bot2, 'chicken')"]
        env.set_human_action("")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = [ "goto(bot2, 'furnace')"]
        env.set_human_action("")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = [ "putItemFurnace(bot2, 'chicken')"]
        env.set_human_action("")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = [""]
        env.set_human_action("I will take the chicken to chest.")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = [""]
        env.set_human_action("")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        actions = [""]
        env.set_human_action("")
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')
        time.sleep(5)
        state = env.step(actions)
        print("Agent Actions: \n")
        print(actions)
        print('***')
        print(state)
        print('***')

    case3()