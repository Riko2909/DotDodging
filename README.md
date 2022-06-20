# DotDodging

## Material
For this Project to work you need:
-  2 Raspberry PIs (3 or 4)
-  4 LED-Matrix 8x8 stacked together
- Python 3

### Python Libarys
- keyboard
- luma
- websockets
- asyncio
## Getting started
Connect the LED-Matrix to the PI and install the headless version of the RaspiOS on the first PI and connect it to your Network. 

Download this Code and run after editing the IP in line **351** :

    sudo python3 test.py 

To start the webserver, simply install apache2 and put the **index.html** into the root directory of the webserver (default: /var/www/html/). 
On the other PI Install [FullPageOS](https://github.com/guysoft/FullPageOS) and also connect it to your Network. Add the current IP-Adress of the PI with the webserver reboot.

## Start playing
If something is displaying on the Matrix, you did everything right. If not, feel free to start an Issue and describe your Problem.

To start/restart just press

> spacebar

 





