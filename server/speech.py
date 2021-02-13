#!/usr/bin/python3

import speech_recognition as sr
import move
import robotLight
from time import ctime
import time
import os
from gtts import gTTS

move.setup()

RL = robotLight.RobotLight()

v_command = ''
speed_set = 80
rad = 0.5
turnWiggle = 60


def setup():
    move.setup()

def respond(audiostring):
    print(audiostring)
    tts = gTTS(text=audiostring, lang='en-US')
    tts.save("speech.mp3")
    os.system("mpg321 speech.mp3")


def listen():
    r = sr.Recognizer()
    with sr.Microphone(device_index = 0, sample_rate = 48000) as source:
        print("I am listening...")
        audio = r.listen(source)
    data = ""
    try:
        data = r.recognize_google(audio)
        print("You said: " + data)
    except sr.UnknownValueError:
        print("Google Speech Recognition did not understand audio")
    except sr.RequestError as e:
        print("Request Failed; {0}".format(e))
    return data

    # print('pre')

    listening = True

    if "how are you" in data:
        listening = True
        respond("I am well")

    elif "what time is it" in data:
        listening = True
        respond(ctime())

    if 'forward' in v_command:
        move.motor_left(1, 0, speed_set)
        move.motor_right(1, 1, speed_set)
        time.sleep(1)
        move.motorStop()

    elif 'backward' in v_command:
        move.motor_left(1, 1, speed_set)
        move.motor_right(1, 0, speed_set)
        time.sleep(1)
        move.motorStop()

    elif 'left' in data:
        listening = True
        move.motor_left(1, 1, speed_set)
        move.motor_right(1, 1, speed_set)
        time.sleep(2)
        move.motorStop()

    elif "right" in data:
        listening = True
        move.motor_left(1, 0, speed_set)
        move.motor_right(1, 0, speed_set)
        time.sleep(2)
        move.motorStop()

    elif "stop listening" in data:
        listening = False
        print('Listening stopped')
        return listening

    else:
        pass
