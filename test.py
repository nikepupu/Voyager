from whisper_mic.whisper_mic import WhisperMic
import queue
import threading
import time

mic = WhisperMic()
audio_queue = queue.Queue()

def listen():
    while True:
        result = mic.listen(2)
        print('result: ', result)
        audio_queue.put_nowait(result)
x = threading.Thread(target=listen, daemon=True).start()

while True:
    continue
