#!/usr/bin/python3
# File name   : speech.py
# Description : Speech Recognition 
# Website     : www.adeept.com
# E-mail      : support@adeept.com
# Author      : William & Authors from https://github.com/Uberi/speech_recognition#readme
# Date        : 2018/10/12
import speech_recognition as sr
import move
import RPIservo
import robotLight
import time

scGear = RPIservo.ServoCtrl()
scGear.moveInit()

move.setup()

RL=robotLight.RobotLight()

v_command=''
speed_set = 80

def setup():
    move.setup()


def run():
    global v_command
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone(device_index =0,sample_rate=48000) as source:
        r.record(source,duration=2)
        #r.adjust_for_ambient_noise(source)
        print("Command?")
        audio = r.listen(source)

    try:
        v_command = r.recognize_sphinx(audio,
        keyword_entries=[('forward',1.0),('backward',1.0),
        ('left',1.0),('right',1.0),('stop',1.0)])        #You can add your own command here
        print(v_command)
    except sr.UnknownValueError:
        print("say again")
    except sr.RequestError as e:
        pass

    #print('pre')

    if 'forward' in v_command:
        move.motor_left(1, 0, speed_set)
        move.motor_right(1, 0, speed_set)
        time.sleep(2)
        move.motorStop()

    elif 'backward' in v_command:
        move.motor_left(1, 1, speed_set)
        move.motor_right(1, 1, speed_set)
        time.sleep(2)
        move.motorStop()

    elif 'left' in v_command:
        move.motor_left(1, 0, speed_set)
        move.motor_right(1, 0, speed_set)
        time.sleep(2)
        move.motorStop()

    elif "right" in v_command:
        move.motor_left(1, 0, speed_set)
        move.motor_right(1, 0, speed_set)
        time.sleep(2)
        move.motorStop()

    elif 'stop' in v_command:
        move.motorStop()

    else:
        pass
