# stingray-bot

## How to connect
- Run `ssh user@raspberrypi` and enter password `pass`
- Plug USB A into Pi and USB C into ESB32
- Plug USB C power brick into Pi
- Plug power tool battery into motor and turn on
- Turn on the Xbox controller
- Run the following in the ssh terminal
```
cd /home/user/Documents/Code/stingray-bot
conda activate stingray
python bluetooth_controller.py
```
- Controller readings should be printing to the terminal