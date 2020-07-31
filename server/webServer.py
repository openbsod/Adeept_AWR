#!/usr/bin/env/python

import time
import threading
import move
import Adafruit_PCA9685
import os
import info
import RPIservo
import servo
import functions
import robotLight
import switch
import socket
import logging
import subprocess
import sys

# websocket
import asyncio
import websockets

# voice assistant
from google.assistant.library.event import EventType
from aiy.assistant import auth_helpers
from aiy.assistant.library import Assistant
from gtts import gTTS

import json
import app

functionMode = 0
speed_set = 100
rad = 0.5
turnWiggle = 60

scGear = RPIservo.ServoCtrl()
scGear.moveInit()

P_sc = RPIservo.ServoCtrl()
P_sc.start()

C_sc = RPIservo.ServoCtrl()
C_sc.start()

T_sc = RPIservo.ServoCtrl()
T_sc.start()

H_sc = RPIservo.ServoCtrl()
H_sc.start()

G_sc = RPIservo.ServoCtrl()
G_sc.start()

# modeSelect = 'none'
modeSelect = 'PT'

init_pwm0 = scGear.initPos[0]
init_pwm1 = scGear.initPos[1]
init_pwm2 = scGear.initPos[2]
init_pwm3 = scGear.initPos[3]
init_pwm4 = scGear.initPos[4]

fuc = functions.Functions()
fuc.start()

curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)


def servoPosInit():
    scGear.initConfig(0, init_pwm0, 1)
    P_sc.initConfig(1, init_pwm1, 1)
    T_sc.initConfig(2, init_pwm2, 1)
    H_sc.initConfig(3, init_pwm3, 1)
    G_sc.initConfig(4, init_pwm4, 1)


def replace_num(initial, new_num):  # Call this function to replace data in '.txt' file
    global r
    newline = ""
    str_num = str(new_num)
    with open(thisPath + "/RPIservo.py", "r") as f:
        for line in f.readlines():
            if line.find(initial) == 0:
                line = initial + "%s" % (str_num + "\n")
            newline += line
    with open(thisPath + "/RPIservo.py", "w") as f:
        f.writelines(newline)


def fpv_thread():
    global fpv
    fpv = FPV.FPV()
    fpv.capture_thread(addr[0])


# def ap_thread():
#    os.system("sudo create_ap wlan0 eth0 Groovy 12345678")


def functionselect(command_input, response):
    global functionMode
    if 'scan' == command_input:
        if modeSelect == 'PT':
            radar_send = fuc.radarScan()
            print(radar_send)
            response['title'] = 'scanResult'
            response['data'] = radar_send
            time.sleep(0.3)

    elif 'findColor' == command_input:
        if modeSelect == 'PT':
            flask_app.modeselect('findColor')

    elif 'motionGet' == command_input:
        flask_app.modeselect('watchDog')

    elif 'stopCV' == command_input:
        flask_app.modeselect('none')
        switch.switch(1, 0)
        switch.switch(2, 0)
        switch.switch(3, 0)

    elif 'police' == command_input:
        RL.police()

    elif 'policeOff' == command_input:
        RL.pause()
        move.motorStop()

    elif 'automatic' == command_input:
        if modeSelect == 'PT':
            fuc.automatic()
        else:
            fuc.pause()

    elif 'automaticOff' == command_input:
        fuc.pause()
        move.motorStop()

    elif 'trackLine' == command_input:
        fuc.trackLine()

    elif 'trackLineOff' == command_input:
        fuc.pause()

    elif 'steadyCamera' == command_input:
        fuc.steady(C_sc.lastPos[4])

    elif 'steadyCameraOff' == command_input:
        fuc.pause()
        move.motorStop()


def switchctrl(command_input, response):
    if 'Switch_1_on' in command_input:
        switch.switch(1, 1)

    elif 'Switch_1_off' in command_input:
        switch.switch(1, 0)

    elif 'Switch_2_on' in command_input:
        switch.switch(2, 1)

    elif 'Switch_2_off' in command_input:
        switch.switch(2, 0)

    elif 'Switch_3_on' in command_input:
        switch.switch(3, 1)

    elif 'Switch_3_off' in command_input:
        switch.switch(3, 0)


def robotctrl(command_input, response):
    global direction_command, turn_command
    if 'forward' == command_input:
        direction_command = 'forward'
        move.move(speed_set, 'forward', 'no', rad)

    elif 'backward' == command_input:
        direction_command = 'backward'
        move.move(speed_set, 'backward', 'no', rad)

    elif 'DS' in command_input:
        direction_command = 'no'
        move.move(speed_set, 'no', 'no', rad)

    elif 'left' == command_input:
        turn_command = 'left'
        move.move(speed_set, 'no', 'left', rad)

    elif 'right' == command_input:
        turn_command = 'right'
        move.move(speed_set, 'no', 'right', rad)

    elif 'TS' in command_input:
        turn_command = 'no'
        if direction_command == 'no':
            move.move(speed_set, 'no', 'no', rad)
        else:
            move.move(speed_set, direction_command, 'no', rad)

    # elif 'lookleft' == command_input:
    #     P_sc.singleServo(0, 1, 3)

    # elif 'lookright' == command_input:
    #     P_sc.singleServo(0, -1, 3)

    # elif 'LRstop' in command_input:
    #     P_sc.stopWiggle()

    elif 'up' == command_input:
        # C_sc.singleServo(0, 1, 3)
        servo.camera_ang('lookup', 'no')
    elif 'down' == command_input:
        # C_sc.singleServo(0, -1, 3)
        servo.camera_ang('lookdown', 'no')
    # elif 'UDstop'==command_input:
    #    #C_sc.stopWiggle()
    #    servo.camera_ang('home','no')
    #    time.sleep(0.2)
    #    servo.clean_all()
    elif 'handup' == command_input:
        H_sc.singleServo(2, 1, 3)

    elif 'handdown' == command_input:
        H_sc.singleServo(2, -1, 3)

    elif 'HAstop' in command_input:
        H_sc.stopWiggle()

    elif 'grab' == command_input:
        G_sc.singleServo(3, -1, 3)

    elif 'loose' == command_input:
        G_sc.singleServo(3, 1, 3)

    elif 'stop' == command_input:
        G_sc.stopWiggle()

    elif 'home' == command_input:
        P_sc.moveServoInit([0])
        C_sc.moveServoInit([4])
        T_sc.moveServoInit([1])
        H_sc.moveServoInit([2])
        G_sc.moveServoInit([3])


def configpwm(command_input, response):
    global init_pwm0, init_pwm1, init_pwm2, init_pwm3, init_pwm4
    if 'SiLeft' == command_input:
        init_pwm0 += 1
        scGear.setPWM(0, init_pwm0)
    elif 'SiRight' == command_input:
        init_pwm0 -= 1
        scGear.setPWM(0, -init_pwm0)
    elif 'PWM0MS' == command_input:
        scGear.initConfig(0, init_pwm0, 1)
        replace_num('init_pwm0 = ', init_pwm0)

    elif 'PWM1MS' == command_input:
        init_pwm1 = P_sc.lastPos[1]
        P_sc.initConfig(1, P_sc.lastPos[1], 1)
        replace_num('init_pwm1 = ', P_sc.lastPos[1])

    elif 'PWM2MS' == command_input:
        init_pwm2 = T_sc.lastPos[2]
        T_sc.initConfig(2, T_sc.lastPos[2], 1)
        print('LLLLLS', T_sc.lastPos[2])
        replace_num('init_pwm2 = ', T_sc.lastPos[2])

    elif 'PWM3MS' == command_input:
        init_pwm3 = H_sc.lastPos[3]
        H_sc.initConfig(3, H_sc.lastPos[3], 1)
        replace_num('init_pwm3 = ', H_sc.lastPos[3])

    elif 'PWM4MS' == command_input:
        init_pwm4 = G_sc.lastPos[4]
        G_sc.initConfig(4, G_sc.lastPos[4], 1)
        replace_num('init_pwm4 = ', G_sc.lastPos[4])

    elif 'PWMINIT' == command_input:
        print(init_pwm1)
        servoPosInit()

    elif 'PWMD' == command_input:
        init_pwm0, init_pwm1, init_pwm2, init_pwm3, init_pwm4 = 300, 300, 300, 300, 300
        scGear.initConfig(0, init_pwm0, 1)
        replace_num('init_pwm0 = ', 300)

        P_sc.initConfig(1, 300, 1)
        replace_num('init_pwm1 = ', 300)

        T_sc.initConfig(2, 300, 1)
        replace_num('init_pwm2 = ', 300)

        H_sc.initConfig(3, 300, 1)
        replace_num('init_pwm3 = ', 300)

        G_sc.initConfig(4, 300, 1)
        replace_num('init_pwm4 = ', 300)


def update_code():
    # Update local to be consistent with remote
    projectpath = thisPath[:-7]
    with open(f'{projectpath}/config.json', 'r') as f1:
        config = json.load(f1)
        if not config['production']:
            print('Update code')
            # Force overwriting local code
            if os.system(
                    f'cd {projectpath} && sudo git fetch --all && sudo git pull') == 0:
                print('Update successfully')
                print('Restarting...')
                os.system('sudo systemctl reboot')


def wifi_check():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 80))
        ipaddr_check = s.getsockname()[0]
        s.close()
        print(ipaddr_check)
        update_code()
    except:
        RL.pause()
        RL.setColor(0, 255, 64)
        #        ap_threading=threading.Thread(target=ap_thread)   #Define a thread for data receiving
        #        ap_threading.setDaemon(True)                      #'True' means it is a front thread
        #        ap_threading.start()                              #Thread starts
        RL.setColor(0, 16, 50)
        time.sleep(1)
        RL.setColor(0, 16, 100)
        time.sleep(1)
        RL.setColor(0, 16, 150)
        time.sleep(1)
        RL.setColor(0, 16, 200)
        time.sleep(1)
        RL.setColor(0, 16, 255)
        time.sleep(1)
        RL.setColor(35, 255, 35)


async def check_permit(websocket):
    while True:
        recv_str = await websocket.recv()
        cred_dict = recv_str.split(":")
        if cred_dict[0] == "admin" and cred_dict[1] == "123456":
            response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
            await websocket.send(response_str)
            return True
        else:
            response_str = "sorry, the username or password is wrong, please submit again"
            await websocket.send(response_str)


async def recv_msg(websocket):
    global speed_set, modeSelect
    move.setup()
    direction_command = 'no'
    turn_command = 'no'

    while True:
        response = {
            'status': 'ok',
            'title': '',
            'data': None
        }

        data = ''
        data = await websocket.recv()
        try:
            data = json.loads(data)
        except Exception as e:
            print('not A JSON')

        if not data:
            continue

        if isinstance(data, str):
            robotCtrl(data, response)

            switchCtrl(data, response)

            functionselect(data, response)

            configPWM(data, response)

            if 'get_info' == data:
                response['title'] = 'get_info'
                response['data'] = [info.get_cpu_tempfunc(), info.get_cpu_use(), info.get_ram_info()]

            if 'wsB' in data:
                try:
                    set_b = data.split()
                    speed_set = int(set_b[1])
                except:
                    pass

            elif 'AR' == data:
                modeSelect = 'AR'
                try:
                    fpv.changeMode('ARM MODE ON')
                except:
                    pass

            elif 'PT' == data:
                modeSelect = 'PT'
                try:
                    fpv.changeMode('PT MODE ON')
                except:
                    pass

            # CVFL
            elif 'CVFL' == data:
                flask_app.modeselect('findlineCV')

            elif 'CVFLColorSet' in data:
                color = int(data.split()[1])
                flask_app.camera.colorSet(color)

            elif 'CVFLL1' in data:
                pos = int(data.split()[1])
                flask_app.camera.linePosSet_1(pos)

            elif 'CVFLL2' in data:
                pos = int(data.split()[1])
                flask_app.camera.linePosSet_2(pos)

            elif 'CVFLSP' in data:
                err = int(data.split()[1])
                flask_app.camera.errorSet(err)

            elif 'defEC' in data:  # Z
                fpv.defaultExpCom()

        elif isinstance(data, dict):
            if data['title'] == "findColorSet":
                color = data['data']
                flask_app.colorFindSet(color[0], color[1], color[2])

        if not functionMode:
            print('Functions OFF')
        else:
            pass

        print(data)
        response = json.dumps(response)
        await websocket.send(response)


async def main_logic(websocket, path):
    await check_permit(websocket)
    await recv_msg(websocket)


def power_off_pi():
    tts.say('Good bye!')
    subprocess.call('sudo shutdown now', shell=True)


def reboot_pi():
    tts.say('See you in a bit!')
    subprocess.call('sudo reboot', shell=True)


def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    tts.say('My IP address is %s' % ip_address.decode('utf-8'))


def process_event(assistant, event):
    if event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        text = event.args['text'].lower()
        if text == 'power off':
            assistant.stop_conversation()
            power_off_pi()
        elif text == 'reboot':
            assistant.stop_conversation()
            reboot_pi()
        elif text == 'ip address':
            assistant.stop_conversation()
            say_ip()
        elif text == 'police':
            assistant.stop_conversation()
            RL.police()
    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)


async def assist():
    credentials = auth_helpers.get_assistant_credentials()
    with Assistant(credentials) as assistant:
        for event in assistant.start():
            process_event(assistant, event)

if __name__ == '__main__':
    switch.switchSetup()
    switch.set_all_switch_off()

    HOST = ''
    PORT = 10223  # Define port serial
    BUFSIZE = 1024  # Define buffer size
    ADDR = (HOST, PORT)

    global flask_app
    flask_app = app.webapp()
    flask_app.startthread()

    try:
        RL = robotLight.RobotLight()
        RL.start()
        RL.breath(70, 70, 255)
    except:
        print(
            'Use "sudo pip3 install rpi_ws281x"')
        pass

    while 1:
        wifi_check()
        try:  # Start server,waiting for client
            start_server = websockets.serve(main_logic, '0.0.0.0', 8888)
            asyncio.get_event_loop().run_until_complete(start_server)
            print('waiting for connection...')
            # print('...connected from :', addr)
            break
        except Exception as e:
            print(e)
            RL.setColor(0, 0, 0)
        try:
            RL.setColor(0, 80, 255)
        except:
            pass
    asyncio.get_event_loop().run_until_complete(assist())
    asyncio.get_event_loop().run_forever()
    try:
        RL.pause()
        RL.setColor(0, 255, 64)
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        print(e)
        RL.setColor(0, 0, 0)
        move.destroy()
