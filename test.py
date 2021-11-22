#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

import random

import keyboard

import asyncio
import websockets

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas

refresh = False



game_objects = {
    "cactus_very_big" : [
        0, 0, 0, 0, 1, 1, 1, 1
    ],
    "cactus_big" : [
        0, 0, 0, 0, 0, 1, 1, 1
    ],
    "cactus_little" : [
        0, 0, 0, 0, 0, 0, 0, 1
    ],
    "bird_jump" : [
        0, 0, 0, 0, 0, 0, 1, 0
    ],
    "bird_crouch" : [
        0, 0, 0, 0, 0, 1, 0, 0
    ],
    "wall" : [
        1, 1, 0, 0, 0, 0, 1, 1
    ]
}

data = ""

class DinoGame:
    def __init__(self):
        self.game_canvas = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.render_matrix = []
        self.score = 0
        self.serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(self.serial, width=32, height=8, block_orientation=-90, rotate=0)
        self.animation_tick = 0
        self.jump_state = 6
        self.object_state = self.device.width - 1
        self.spawnspeed = 5
        self.spawnquantity = 23
        self.jumping = False

        self.jumpanimationtick = 0

        self.fall = False

        self.playerPos = []

        self.speed = 0.01
        # self.speed = 0.05

    # Spielerpunkte zurückgeben
    def get_PlayerScore(self):
        return self.score


    
    # Objekte aus der Rendermatrix filtern
    def filter_RenderMatrix_to_Objects(self):

        temp_obj = self.render_matrix

        if self.playerPos[0] in temp_obj:
            temp_obj.remove(self.playerPos[0])
        
        if self.playerPos[1] in temp_obj:
            temp_obj.remove(self.playerPos[1])

        return temp_obj

    # Überprüfen ob der Spieler mit einem Objekt kollidiert ist
    def is_collided(self):

        object_matrix = self.filter_RenderMatrix_to_Objects()

        for object_cord in object_matrix:

            # TODO: Check if Object is:
            #
            # X O  <--
            # P X
            # P X

            # Check if Object X - 1 is PlayerUP X and Object Y is PlayerUP Y
            if object_cord[0] - 1 == self.playerPos[0][0] and object_cord[1] == self.playerPos[0][1] + 1:
                print("XD")
                return True

            # Check if Object X - 1 is PlayerUP X and Object Y is PlayerUP Y
            if object_cord[0] - 1 == self.playerPos[0][0] and object_cord[1] == self.playerPos[0][1]:
                print("FACE")
                return True

            # Check if Object X - 1 is PlayerDOWN X and Object Y is PlayerDOWN Y
            if object_cord[0] - 1 == self.playerPos[1][0] and object_cord[1] == self.playerPos[1][1]:
                print("FOOT")
                return True

            # Check if Object Y - 1 is PlayerDOWN Y and Object X is PlayerDOWN X
            if object_cord[1] - 1 == self.playerPos[1][1] and object_cord[0] == self.playerPos[1][0]:
                print("BOTTOM")
                return True
            
            # Check if Object Y + 1 is PlayerDOWN Y and Object X is PlayerDOWN X
            if object_cord[1] + 1 == self.playerPos[1][1] and object_cord[0] == self.playerPos[1][0]:
                print("TOP")
                return True

        return False


    def move_objects(self):

        if self.animation_tick % self.spawnspeed == 0:

            rmd_obj = random.choice(list(game_objects.keys()))

            for i in range(8):

                if self.is_collided():
                    return False

                self.game_canvas[i].pop(0)
              
                if self.object_state == 0:

                    self.game_canvas[i].append(
                        game_objects[rmd_obj][i]
                    )

            else:
                for i in range(8):
                    self.game_canvas[i].append(0)
            

        if self.animation_tick % self.spawnspeed == 0:
            self.object_state = (self.object_state - 1) % self.spawnquantity

        #print("-------------------")
        #print(self.game_canvas[7])
        #print(self.game_canvas[6])
        #print(self.game_canvas[5])
        #print(self.game_canvas[4])
        #print(self.game_canvas[3])

        return True

    def player_jump(self):
        # print(self.animation_tick, end="\r")
        # print(self.jump_state)
        
        # print(self.jumpanimationtick)

        if not self.jumping:
            self.jumping = True
        
        if self.jumpanimationtick < 50:
            
            for i in range(self.jump_state, self.jump_state + 1):
                
                #                  y    x
                self.game_canvas[i - 1][2] = 0
                self.game_canvas[i    ][2] = 0
                self.game_canvas[i + 1][2] = 0

                self.game_canvas[i - 1][3] = 1
                self.game_canvas[i    ][3] = 1
                self.game_canvas[i + 1][3] = 0

                self.playerPos = [
                    [3, i-1],
                    [3, i  ]
                ]

            if self.jumpanimationtick % 10 == 0 and self.fall == True:
                self.jump_state = (self.jump_state - 1)

            self.fall = True
            
        else:

            for i in range(self.jump_state, self.jump_state + 1):
                
                #                  y    x
                self.game_canvas[i - 1][2] = 0
                self.game_canvas[i    ][2] = 0
                self.game_canvas[i + 1][2] = 0

                self.game_canvas[i - 1][3] = 0
                self.game_canvas[i    ][3] = 1
                self.game_canvas[i + 1][3] = 1

                self.playerPos = [
                #    x  y
                    [3, i],
                    [3, i+1]
                ]
            
            if self.jumpanimationtick % 10 == 0 and self.fall == False:
                self.jump_state = (self.jump_state + 1)

            if self.jump_state == 6:
                self.game_canvas[5][3] = 0
                self.jumping = False

            self.fall = False

    def player_stay(self):

        self.game_canvas[6][2] = 0
        self.game_canvas[7][2] = 0

        self.game_canvas[6][3] = 1
        self.game_canvas[7][3] = 1

        self.playerPos = [
                [3, 6],
                [3, 7]
        ]

        # print("stay")

    def get_renderFields(self):
        self.render_matrix = []
        for y in range(self.device.height):
            for x in range(self.device.width):   
                if self.game_canvas[y][x] == 1:
                    self.render_matrix.append([x, y])


    def render_Fields(self):
        self.get_renderFields()
        with canvas(self.device) as draw:
            for x, y in self.render_matrix:
                draw.point((x, y), fill="red")

    async def game_loop(self):

        print("Created device")

        global refresh
        global data

        try:
            while True:

                if round(self.score, 3) % 2 == 0:
                    self.speed = self.speed - 0.0001

                self.render_Fields()
                
                #time.sleep(0.005)
                await asyncio.sleep(self.speed)

                self.animation_tick = (self.animation_tick + 1) % 100

                if self.animation_tick % 10:
                    self.score = self.score + 0.01
                    data = f"false,{round(self.get_PlayerScore(), 3)}"
                    refresh = True

                if not self.move_objects():
                    data = f"true,{round(self.get_PlayerScore(), 3)}"
                    refresh = True
                    return 0

                if keyboard.is_pressed('space') or keyboard.is_pressed('enter') or self.jumping:

                    self.jumpanimationtick  = (self.jumpanimationtick + 1) % 100

                    # print(self.jumping)
                    self.player_jump()
                elif not self.jumping:
                    self.jumpanimationtick = 0
                    self.player_stay()
                
        except KeyboardInterrupt:
            return 1


async def bums(websocket, path):

    global refresh
    global data

    while True:
    
        if refresh is True:
                await websocket.send(data)

                # print("Sending")
                
                refresh = False

        await asyncio.sleep(0.01)

async def main():
    play = True

    global refresh
    global data

    while play:

        os.system("clear")

        game = DinoGame()

        if await game.game_loop():
            print("Spiel beendet", end="\n\n")
            print(game.get_PlayerScore())

            data = f"true,{round(game.get_PlayerScore(), 3)}"

            refresh = True
        else:
            
            print("Du bist gestorben", end="\n\n")
            print("Punkte", round(game.get_PlayerScore(), 3))

        

        while not keyboard.is_pressed('space'):
            await asyncio.sleep(0.001)
        


socketserver = websockets.serve(bums, "172.16.16.105", 6332)

if __name__ == "__main__":

    asyncio.get_event_loop().run_until_complete(socketserver)
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()