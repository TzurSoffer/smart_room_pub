# <span style="font-size:2em;">Smart Room Control System</span>

# <span style="color:red; font-size:1.5em;">[WARNING] This repo is in development</span>

# <span style="font-size:1.5em;">Overview</span>
The Smart Room Control System is a Python-based application that manages various devices in a room, including lights, led strips, sensors, and more. The application is based on a "room manger", which routes all traffic and provides a database for all app to seamlessly sync variables, even if they are not directly connected, this means that every module in this app could run a on a different machine without any issues. This app is build around MQTT and ArduBridge.

The smart-room is a project I have been working on for the past few years and this is the public release of it. Due to my project having many private files committed and pushed over time, I am unable publish it and instead, I had to clean it up and publish it under a different repo. 

# <span style="font-size:1.5em;">Features</span>
 - Light Control:
Adjust brightness and toggle lights using buttons, remote control, or MQTT commands.

- Camera security system.

- Double clap for turing lights on/off

- Automatic shutoff of lights once you leave the room.

- Led strip for more efficient lighting.

- Remote gui that works on windows, linux, and even android.

- MQTT Communication:
Receive and process commands from specified MQTT topics.
Log events and send updates via MQTT.

- Arduino Integration:
Connects to Arduino for hardware-level interactions such as GPIO control and PWM output.


# <span style="font-size:1.5em;">Parts List</span>
## For the dimmer lights:
- MG90S Servo
- Single pole light dimmer
- Metal rod (straightened paper clip)
- [Linkage Stopper](https://www.amazon.com/Hobbypark-Adjustable-Connector-Stoppers-Airplane/dp/B01EE6W2TW?crid=1BF87KDGXRLKT&dib=eyJ2IjoiMSJ9.Juz2pHjLWpUisf17gZex4TIEm4HkT_AUmRX313brXCK9X1mMCl46533ySVbu3JhTi5RHZWPE0gl5h3J0emMhGtS7LrOhMlSxP1GPix-ldoJxwf_jv_13FvJ_v-vG7wgqYrBx1gvokptivT8rSIWcbOqcwmMrIFqujD_VIY_KQbPsPuCbW8lAG8wvfI29lKGoooUndg5B5fWgSskfcG1o8w.aMaJ4WH_wLAjr-rRh-ND6zwac9R7z_ELACLzUsZdKkQ)
- Light switch cover (3D printer file supplied in the CAD folder, if no 3D printer is available, you will just have to glue the servo to the light switch cover)
- Light Switch-to-Servo connector (3D printer file supplied in the CAD folder, if no 3D printer is available, you will have to again, use glue)
## For LED strip:
- WS2812B Led Strip (I am using and tested [BTF-LIGHTING LED Strip](https://www.amazon.com/BTF-LIGHTING-Individual-Addressable-300Pixels-Non-Waterproof/dp/B088BPGMXB?crid=Z1E6PQ4EDAH4&dib=eyJ2IjoiMSJ9.Ry6dXdc6yCTZcKoG4aJ3Th8LGYA5Gy4D9YRD3VKxIgLerv9UEdIo9LzjM5warJ15IOo3UipmvCMalIuG37O4sba4S1yJfIl_pFJ2PmyNYdtAQZ7zwy2TlwIzyOsDDSvyJSW842Jrq8QzkYw1O5iXkYojdHplqJk_acgI3oAclXQTHIdhtTVCH71XX5p0TUTZRqhaAX7-aL-bqYAPMInolPyhTi8YwSEKCQrsjHAMCzQCk-DpFkixaZo2NMuVuC21OAPn214TfKL4JSGFKlYXaV6wbLQfugfu4gICaakYJOg.h9Q7bcdqLQ5Cf8dQFsqAUVJwtS4rA7UqDafByJGWurU&dib_tag=se))
- Strong power supply
## For GUI
Any windows, linux, mac, or android device. My GUI attachment has been designed for the [YQSAVIOR Q2 Tablet](https://www.amazon.com/dp/B09LHMMJ2Q?ref=cm_sw_r_apan_dp_3CRTS086MC9D8FX62A8X&ref_=cm_sw_r_apan_dp_3CRTS086MC9D8FX62A8X&social_share=cm_sw_r_apan_dp_3CRTS086MC9D8FX62A8X&starsLeft=1&skipTwisterOG=1&th=1)

# <span style="font-size:1.5em;">Installation</span>

## (RECOMMENDED) Installing software via Docker
### 1. Clone this repository:

``` bash
git clone https://github.com/TzurSoffer/smart_room_pub.git
cd smart_room_pub
```

### 2. build the container
```bash
sudo docker build -t smart-room .
```

### 3. deploy via docker-compose

Run the command ```sudo docker-compose up -d``` to start the room.

### 4. Give your smart-room a static ip
- For windows, you can follow [this guide.](https://www.youtube.com/watch?v=fQ4acV76XPc)
- For linux, you can follow [this guide.](https://www.jeffgeerling.com/blog/2024/set-static-ip-address-nmtui-on-raspberry-pi-os-12-bookworm)
- NOTE: not every linux machine uses the same network manager, and if the guide does not work for you, please search up how to setup a static ip on your specific flavor of linux.
- NOTE: This it not the best method for setting up a static ip, it will always be better to set it up through your router.

## Installing software via python

### 1. Clone this repository:

``` bash
git clone https://github.com/TzurSoffer/smart_room_pub.git
cd smart_room_pub
```

### 2. Install dependencies:

``` bash
pip install -r requirements.txt
```
- if on linux, then also run the commands ```sudo apt install -y portaudio19-dev``` for clap-detector deps.

### 4. setup an mqtt server
- For windows, download and install an mqtt broker from [https://mosquitto.org/download](mosquitto)
- For Linux, run ```sudo apt install -y mosquitto``` to install mosquitto.

### 5. Give your smart-room a static ip
- For windows, you can follow [this guide.](https://www.youtube.com/watch?v=fQ4acV76XPc)
- For linux, you can follow [this guide.](https://www.youtube.com/watch?v=NjmcUYLmhj0)
- NOTE: not every linux machine uses the same network manager, and if the guide does not work for you, please search up how to setup a static ip on your specific flavor of linux.
- NOTE: This it not the best method for setting up a static ip, it will always be better to set it up through your router.

## Connecting arduino
- Take an official arduino uno (Revision 3 has been tested), and connect it via usb to the rpi. If you have already flashed it with the correct firmware, it should automatically be detected by the software and start flashing an LED after the smart-room has been started. If you did not flash it with the firmware, please look below at the flashing section.
### If the smart-room is not detecting your arduino, you need to find your arduino port.
- for linux, run this command:
```bash
python -c "import serial.tools.list_ports; [print(f'Port: {port.device}, Description: {port.description}, HWID: {port.hwid}') for port in serial.tools.list_ports.comports()]"
```
- for windows, go to device manager and find your arduino under the COM ports section.
- Once you found your arduino's port, put its port into the settings file under the ```arduComport``` variable. ex. ```COM7``` for windows or ```/dev/ttyACM0``` for linux.

## Flashing arduino with correct firmware
### If only one arduino is connected and you are using the docker image.
- In the ```settings.json``` file, change the ```arduFirmwareNoPromptUpdate``` variable to ```true```. This will flash the arduino with the correct firmware on start of app. Then simply start the app using ```sudo docker-compose up -d```, and after a bit, the arduino LEDs should turn on for a few seconds, then stop, then begin flashing. This is how you know the arduino has been flashed and the room is running.
### If more than one arduino is connected or the previous step didn't work.
- Connect your Arduino device to a system.
- Follow instructions from [GSOF_ArduBridge](https://github.com/mrGSOF/arduBridge) to flash the arduino with the correct firmware.

# <span style="font-size:1.5em;">Connecting Servo/LEDs/buttons to arduino</span>
# Installing the servo lights:
- Print the [lights cover](./CAD/stls/lightCoverBasic.stl) file and the [light cap](./CAD/stls/lightCoverBasic.stl) file.
- Replace you existing light cover with the printed one.
- use a bit of hot glue to connect the light cap to the light switch.
- Insert the servo into its slot.
- Screw the linkage stopper to the cap.
- connect your metal rod between the arduino and the cap.
- connect the servo to the correct arduino pin (defaults to pin 11 in the core's config).
# Installing the LEDs.
- Connect your LED strip's power cable to an external power supply, the ground to the arduino's ground and the data pin to the correct data pin on the arduino (defaults to pin 13 in the room manager's config)
- Change the ```ledCount``` variable in the room manager's config to the correct LED count.

# <span style="font-size:1.5em;">Setting up GUI</span>
## Installation
- For running on a windows, linux, or mac simply install the requirements using ```pip install -r requirements.txt```, then run the ```main.py``` python file.
- For running on an android device such as a tablet or phone, I have provided the compiled apk file in the bin directory, simply copy the file to your android device, and install it via your file manager or adb.
## Navigation
This GUI has multiple pages each designed for its own section of the room. To switch between pages, click on the page you want from the left hand side of your device and the app will switch your page. To get into the admin panel, click it and input the password.

# <span style="font-size:1.5em;">Adding a module</span>
### Publishing messages to room controller
- Once you have developed your module and want to use incorporate into your room, you need set it up in the settings file of the roomManager. Note, make sure you are using the ```mqttCommunication.py``` file and not the regular ```paho-mqtt``` for sending messages to the server.
    - in the features key of the setting, add a new entry following this pattern:
    ```json
    "inputTopic": {
        "commands": {
            "msgContent": "commandCallback",
            "msgContent": "commandCallback"
        }
    }
    ```
    replace ```inputTopic``` with the topic that your module will send messages to, ```msgContent``` with the content of the message that gets sent, and ```commandCallback``` with the command you want to call (commands are also specified in the settings file).
    
    - If needed, add a command to the settings file. To add a command, add a new entry in the commands section of the settings following this pattern:
    ```json
    "commandName": {
        "command": "commandType",
        "cmdKey": "cmdValue",
        "cmdKey": "cmdValue"
    }
    ```
    replace ```commandName``` with the name of the command (```commandCallback``` if following instruction from previous step), ```commandType``` with the type of command, your options are between ```sendMessage```, and ```runCommands```, lastly replace cmd cmdKey with the expected keys for said command and command value with a value.

    If adding a ```sendMessage``` command, follow this syntax:
    ```json
    "commandName": {
        "command": "sendMessage",
        "topic": "yourTopic",
        "message": "yourValue"
    }
    ```

    If adding a ```runCommands``` command, follow this syntax:
    ```json
    "commandName": {
        "command": "runCommands",
        "commands": ["cmd1", "cmd2", ...],
    }
    ```

### Listening to messages from the roomManager.
- Follow the previous step for setting up a command, except you want to set the commands topic to be the topic you are listening on.
- Set up a feature that redirect the traffic that you want to receive to the command you made.

### Accessing database variables
Use the ```database.py``` module from the modules folder and create a new instance, then simply pretend your wanted variable exists, and once you try and access it, it will fetch it in the background.
```python
db = DatabaseClient("brokerIp")
db.a = "anything"
print(db.a)
```
you can now close the program or just run in on a different machine, once you try and fetch the variable a, it will still be the value of what you last set it.

# LICENSE
This project is licensed under the MIT License. See the LICENSE file for more details.

# Author
Developed by Tzur Soffer (2021-now).