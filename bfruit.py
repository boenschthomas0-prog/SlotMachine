#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Written by Balázs Nagy <nxbalazs@gmail.com>
# Design by Ferenc Nagy <nferencfx@gmail.com>
# Project web site: http://bfruit.sf.net

import pygame
from pygame.locals import *
from random import randrange
import sys
from sys import argv
from getopt import getopt, GetoptError
import time
import os

VERSION = "0.1.2"

# EG Starts -> Joystick Button Mapping (DragonRise Generic USB Joystick, 12 Buttons)
JOY_TO_KEY = {
    0: pygame.K_7,   # EG Button 1  -> HELP
    1: pygame.K_1,   # EG Button 2  -> BET UP
    2: pygame.K_2,   # EG Button 3  -> BET DOWN
    3: pygame.K_5,   # EG Button 4  -> +5 Credits
    4: pygame.K_6,   # EG Button 5  -> MAX BET
    5: pygame.K_4,   # EG Button 6  -> +5 Credits
    6: pygame.K_8,   # EG Button 7  -> COLLECT
    7: pygame.K_9,   # EG Button 8  -> EXIT
    8: pygame.K_0,   # EG Button 9  -> ESCAPE
    9: pygame.K_0,   # EG Button 10 -> ESCAPE
    10: pygame.K_9,  # EG Button 11 -> EXIT
    11: pygame.K_3,  # EG Button 12 -> SPIN
}

# Aktionen (referenziert von Tastatur + Joystick)
EG_BET_UP = pygame.K_1
EG_BET_DOWN = pygame.K_2
EG_SPIN = pygame.K_3
EG_ADD_CREDIT = pygame.K_4
EG_ADD_CREDIT2 = pygame.K_5
EG_MAX_BET = pygame.K_6
EG_HELP = pygame.K_7
EG_COLLECT = pygame.K_8
EG_EXIT = pygame.K_9
EG_ESCAPE = pygame.K_0

# Slot-Konfiguration
NUM_COLS = 5
NUM_ROWS = 3
SYMB_W = 100
SYMB_H = 100
GAP = 2
NUM_SYMBOLS = 8
SCREEN_W = 800
SCREEN_H = 600
REEL_X0 = 15
REEL_Y0 = 50
COL_W = SYMB_W + GAP
ROW_H = SYMB_H + GAP

# Gewinnlinien (3er-Blöcke über die Walzen)
WIN_LINES = [
    [0, 3, 6],      # obere Reihe Cols 0-2
    [1, 4, 7],      # mittlere Reihe Cols 0-2
    [2, 5, 8],      # untere Reihe Cols 0-2
    [3, 6, 9],      # obere Reihe Cols 1-3
    [4, 7, 10],     # mittlere Reihe Cols 1-3
    [5, 8, 11],     # untere Reihe Cols 1-3
    [6, 9, 12],     # obere Reihe Cols 2-4
    [7, 10, 13],    # mittlere Reihe Cols 2-4
    [8, 11, 14],    # untere Reihe Cols 2-4
    [0, 4, 8],      # Diagonale Cols 0-2
    [2, 4, 6],      # Diagonale Cols 0-2
    [3, 7, 11],     # Diagonale Cols 1-3
    [5, 7, 9],      # Diagonale Cols 1-3
    [6, 10, 14],    # Diagonale Cols 2-4
    [8, 10, 12],    # Diagonale Cols 2-4
]
NUM_WIN_LINES = len(WIN_LINES)

# main menu###########################
class Menu:
    def __init__(self):
        self.screen = screen
        self.maincolor = [0, 0, 0]
        self.white = [255, 255, 255]
        self.bsound = pygame.mixer.Sound("data/sounds/CLICK10A.WAV")
        self.background = pygame.image.load("data/menubg/menubg.png")
        self.backgroundadded = pygame.image.load("data/menubg/added.png")
        self.sav = pygame.image.load("data/menubg/sav.png")
        self.highscore = (pygame.image.load("data/menubg/highscore.png"))
        self.menu = ["  New Game  ", "  Settings  ", "  High score  ", "  Exit to Linux "]
        self.menubg = []
        self.menubg.append(pygame.image.load("data/menubg/al.png").convert())
        self.menubg.append(pygame.image.load("data/menubg/ci.png").convert())
        self.menubg.append(pygame.image.load("data/menubg/he.png").convert())
        self.menubg.append(pygame.image.load("data/menubg/na.png").convert())
        self.menubg.append(pygame.image.load("data/menubg/di.png").convert())
        self.menuall = ""
        self.selectedmenu = 0
        self.mid = []
        # get menu width
        self.menuid()
        # all menu in one:
        self.listmenuall()
        # mainloop
        sz = 0
        szam = 0
        szamlalo = 0
        self.showhs = False # show hs in menu
        while True:
            for self.event in pygame.event.get():
                if self.event.type == pygame.JOYBUTTONDOWN:
                    k = JOY_TO_KEY.get(self.event.button)
                    if k is not None:
                        self.event = pygame.event.Event(pygame.KEYDOWN, key=k)
                if self.selectedmenu == 2:
                    self.showhs = True
                else:
                    self.showhs = False
                if self.event.type == pygame.QUIT:
                    exit()
                if self.event.type == pygame.KEYDOWN:
                    self.bsound.play()
                    if self.event.key in (pygame.K_LEFT, EG_BET_DOWN):
                        if self.selectedmenu == 0:
                            self.selectedmenu = len(self.menu)-1
                        else:
                            self.selectedmenu = self.selectedmenu-1
                    elif self.event.key in (pygame.K_RIGHT, EG_BET_UP):
                        if self.selectedmenu == len(self.menu)-1:
                            self.selectedmenu = 0
                        else:
                            self.selectedmenu = self.selectedmenu+1
                    elif self.event.key in (pygame.K_RETURN, EG_SPIN):
                        if self.selectedmenu == 0:
                            plc = Game()
                        elif self.selectedmenu == 1:
                            plc = Settings()
                        elif self.selectedmenu == 2:
                            self.selectedmenu = 2 # :)
                        else:
                            exit()
                    if self.event.key in (pygame.K_ESCAPE, EG_ESCAPE, EG_EXIT):
                        exit()
            # 1st layer: background color
            self.screen.fill(self.maincolor)
            self.bg = self.menubg[szam]
            self.bg.set_alpha(sz)
            self.screen.blit(self.bg, (0, 0))
            self.screen.blit(self.backgroundadded, (0, 0))
            # 2nd layer: menus
            self.crt_menu()
            # 3rd layer: transparent image
            self.screen.blit(self.background, (0, 0))
            
            font = pygame.font.Font("data/LiberationSans-Regular.ttf", 15)
            text_surface = font.render("Balazs Nagy - BFruit - "+VERSION , True, self.white)
            self.screen.blit(text_surface, (3, 460))
            
            if self.showhs == True:
                self.screen.blit(self.sav, (0, 60))
                self.screen.blit(self.sav, (0, 120))
                self.screen.blit(self.highscore, (50, 60))
                font=pygame.font.Font("data/LiberationSans-Regular.ttf", 25)
                text_surface = font.render(scr, True, self.white)
                self.screen.blit(text_surface, (295, 110))
            
            szamlalo = szamlalo + 4
            
            if szamlalo < 245:
                sz = sz + 4
            if szamlalo > 244:
                sz = sz - 4
                
            if szamlalo > 490:
                sz = 0
                szamlalo = 0
                if szam == len(self.menubg)-1:
                    szam = 0
                else:
                    szam = szam + 1
            
            
            pygame.display.update()
             
            
    def menuid(self):
        for n in self.menu:
            font = pygame.font.Font("data/LiberationSans-Regular.ttf", 25)
            text_surface = font.render(n, True, self.white)
            self.mid.append(text_surface.get_width())
            
    def listmenuall(self):
        for n in self.menu:
            self.menuall = self.menuall+n
            
    def crt_menu(self):
        nmb = 0
        xpos = 0
        while nmb <= self.selectedmenu:
            xpos = xpos-self.mid[nmb]
            nmb = nmb+1
        xpos = xpos+self.mid[self.selectedmenu]/2
        # draw menus on screen
        font = pygame.font.Font("data/LiberationSans-Regular.ttf", 25)
        text_surface = font.render(self.menuall, True, self.white)
        self.screen.blit(text_surface, (320+xpos, 15))

# Settings menu################################
class Settings:
    def __init__(self):
        self.screen = screen
        self.maincolor = [0, 0, 0]
        self.white = [255, 255, 255]
        self.bsound = pygame.mixer.Sound("data/sounds/CLICK10A.WAV")
        self.background = pygame.image.load("data/menubg/menubg.png")
        self.backgroundadded = pygame.image.load("data/menubg/added.png")
        self.sav = pygame.image.load("data/menubg/sav.png")
        self.menu = ["  Fullscreen  ", "  Back to main  "]
        self.menubg = []
        self.menubg.append(pygame.image.load("data/menubg/al.png").convert())
        self.menubg.append(pygame.image.load("data/menubg/ci.png").convert())
        self.menubg.append(pygame.image.load("data/menubg/he.png").convert())
        self.menubg.append(pygame.image.load("data/menubg/na.png").convert())
        self.menubg.append(pygame.image.load("data/menubg/di.png").convert())
        self.menuall = ""
        self.selectedmenu = 0
        self.mid = []
        # get menu width
        self.menuid()
        # all menu in one:
        self.listmenuall()
        # mainloop
        sz = 0
        szam = 0
        szamlalo = 0
        while True:
            for self.event in pygame.event.get():
                if self.event.type == pygame.JOYBUTTONDOWN:
                    k = JOY_TO_KEY.get(self.event.button)
                    if k is not None:
                        self.event = pygame.event.Event(pygame.KEYDOWN, key=k)
                if self.event.type == pygame.QUIT:
                    exit()
                if self.event.type == pygame.KEYDOWN:
                    self.bsound.play()
                    if self.event.key in (pygame.K_LEFT, EG_BET_DOWN):
                        if self.selectedmenu == 0:
                            self.selectedmenu = len(self.menu)-1
                        else:
                            self.selectedmenu = self.selectedmenu-1
                    elif self.event.key in (pygame.K_RIGHT, EG_BET_UP):
                        if self.selectedmenu == len(self.menu)-1:
                            self.selectedmenu = 0
                        else:
                            self.selectedmenu = self.selectedmenu+1
                    elif self.event.key in (pygame.K_RETURN, EG_SPIN):
                        if self.selectedmenu == 0:
                            pygame.display.toggle_fullscreen()
                        else:
                            plc = Menu()
                    if self.event.key in (pygame.K_ESCAPE, EG_ESCAPE, EG_EXIT):
                        exit()
            # 1st layer: background color
            self.screen.fill(self.maincolor)
            self.bg = self.menubg[szam]
            self.bg.set_alpha(sz)
            self.screen.blit(self.bg, (0, 0))
            self.screen.blit(self.backgroundadded, (0, 0))
            # 2nd layer: menus
            self.crt_menu()
            # 3rd layer: transparent image
            self.screen.blit(self.background, (0, 0))
            
            font = pygame.font.Font("data/LiberationSans-Regular.ttf", 15)
            text_surface = font.render("Balazs Nagy - BFruit - "+VERSION , True, self.white)
            self.screen.blit(text_surface, (3, 460))
            
            szamlalo = szamlalo + 4
            
            if szamlalo < 245:
                sz = sz + 4
            if szamlalo > 244:
                sz = sz - 4
                
            if szamlalo > 490:
                sz = 0
                szamlalo = 0
                if szam == len(self.menubg)-1:
                    szam = 0
                else:
                    szam = szam + 1
            
            
            pygame.display.update()
            
    def menuid(self):
        for n in self.menu:
            font = pygame.font.Font("data/LiberationSans-Regular.ttf", 25)
            text_surface = font.render(n, True, self.white)
            self.mid.append(text_surface.get_width())
            
    def listmenuall(self):
        for n in self.menu:
            self.menuall = self.menuall+n
            
    def crt_menu(self):
        nmb = 0
        xpos = 0
        while nmb <= self.selectedmenu:
            xpos = xpos-self.mid[nmb]
            nmb = nmb+1
        xpos = xpos+self.mid[self.selectedmenu]/2
        # draw menus on screen
        font = pygame.font.Font("data/LiberationSans-Regular.ttf", 25)
        text_surface = font.render(self.menuall, True, self.white)
        self.screen.blit(text_surface, (320+xpos, 15))

# the game###########################
class Game:
    def __init__(self):
        self.mut = 0
        self.wins = [0] * NUM_WIN_LINES
        self.keys = 1
        self.credit = 20
        self.bet = 1
        self.lastwin = 0
        self.show = []
        self.npos = NUM_COLS * NUM_ROWS

        self.screen = screen

        self.bsound = pygame.mixer.Sound("data/sounds/CLICK10A.WAV")
        self.rollsound = pygame.mixer.Sound("data/sounds/film_projector.wav")
        self.bgsound = pygame.mixer.Sound("data/sounds/background001.wav")
        self.beepsound = pygame.mixer.Sound("data/sounds/beep.wav")

        self.background = pygame.Surface((SCREEN_W, SCREEN_H))
        self.background.fill([10, 10, 30])
        pygame.draw.rect(self.background, [40, 40, 80],
                         (REEL_X0 - 4, REEL_Y0 - 4,
                          NUM_COLS * COL_W + 8, NUM_ROWS * ROW_H + 8), 0, 8)

        self.raw_imgs = []
        for i in range(1, NUM_SYMBOLS + 1):
            img = pygame.image.load(f"data/img/{i}.png")
            self.raw_imgs.append(pygame.transform.scale(img, (SYMB_W, SYMB_H)))

        self.bgsound.play(loops=-1)
        self.randi()

        while True:
            self.screen.fill([0, 0, 0])
            self.screen.blit(self.background, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    k = JOY_TO_KEY.get(event.button)
                    if k is not None:
                        event = pygame.event.Event(pygame.KEYDOWN, key=k)
                if event.type == pygame.QUIT:
                    self.bgsound.stop()
                    exit()
                if event.type == pygame.KEYDOWN:
                    self.bsound.play()
                    if event.key in (pygame.K_LEFT, EG_SPIN) and self.keys == 1:
                        if self.credit > 0:
                            if self.credit - self.bet < 0:
                                self.bet = self.credit
                            self.credit = self.credit - self.bet
                            self.randi()
                            self.roll()
                            self.winner()
                        elif self.credit == 0 and self.bet == 0:
                            self.bgsound.stop()
                            plc = Menu()
                    if self.credit > 0:
                        if event.key in (pygame.K_UP, EG_BET_UP) and self.keys == 1:
                            if self.credit - self.bet - 1 >= 0:
                                self.bet = self.bet + 1
                            else:
                                self.bet = 1
                            if self.bet == 11:
                                self.bet = 1
                        elif event.key == EG_BET_DOWN and self.keys == 1:
                            if self.bet > 1:
                                self.bet = self.bet - 1
                            else:
                                self.bet = 1
                        elif event.key == EG_MAX_BET and self.keys == 1:
                            self.bet = min(self.credit, 10)
                    else:
                        self.bet = 0
                    if event.key in (EG_ADD_CREDIT, EG_ADD_CREDIT2):
                        self.credit = self.credit + 5
                    if event.key in (pygame.K_F1, EG_HELP):
                        if self.keys == 1:
                            self.keys = 0
                            self.menu = "h"
                        elif self.keys == 0:
                            self.keys = 1
                            self.menu = "n"
                    if event.key in (pygame.K_RETURN, EG_COLLECT):
                        self.keys = 0
                        self.menu = "e"
                    if event.key in (pygame.K_ESCAPE, EG_EXIT, EG_ESCAPE) and self.keys == 1:
                        self.bgsound.stop()
                        plc = Menu()

            self.draw_side()
            if self.mut == 1:
                self.drawl()
                self.check()
                self.wins = [0] * NUM_WIN_LINES
            if self.credit == 0 and self.bet == 0:
                font = pygame.font.Font("data/LiberationSans-Regular.ttf", 55)
                ts = font.render("Game Over", True, [255, 0, 0])
                self.screen.blit(ts, (70, 190))

            if self.keys == 0 and self.menu == "h":
                self.helpmenu()
            if self.keys == 0 and self.menu == "e":
                self.endthegame(scr)

            pygame.display.update()

    def col_x(self, col):
        return REEL_X0 + col * COL_W

    def row_y(self, row):
        return REEL_Y0 + row * ROW_H

    def roll(self):
        rs = []
        roll_ticks = []
        last = randrange(5, 9)
        for c in range(NUM_COLS):
            last = randrange(last + 1, last + 4)
            roll_ticks.append(last)
            frames = []
            for r in range(NUM_ROWS):
                idx = c * NUM_ROWS + r
                frames.append(self.raw_imgs[int(self.show[idx]) - 1])
            for _ in range(roll_ticks[c] - NUM_ROWS):
                frames.append(self.raw_imgs[randrange(0, NUM_SYMBOLS)])
            for r in range(NUM_ROWS):
                idx = c * NUM_ROWS + r
                frames.append(self.raw_imgs[int(self.showold[idx]) - 1])
            self.rollsound.play()
            rs.append(frames)

        ptrs = [len(f) - 1 for f in rs]

        while ptrs[NUM_COLS - 1] > NUM_ROWS - 1:
            self.screen.fill([0, 0, 0])
            self.screen.blit(self.background, (0, 0))
            for c in range(NUM_COLS):
                x = self.col_x(c)
                if ptrs[c] > NUM_ROWS - 1:
                    for r in range(NUM_ROWS):
                        self.screen.blit(rs[c][ptrs[c] - (NUM_ROWS - 1 - r)],
                                         (x, self.row_y(r)))
                    ptrs[c] = ptrs[c] - 1
                    rs[c].pop(len(rs[c]) - 1)
                else:
                    for r in range(NUM_ROWS):
                        self.screen.blit(rs[c][ptrs[c] - (NUM_ROWS - 1 - r)],
                                         (x, self.row_y(r)))
            self.draw_side()
            pygame.display.update()

    def draw_side(self):
        sx = REEL_X0 + NUM_COLS * COL_W + 30
        digifont = pygame.font.Font("data/DIGITAL2.ttf", 24)
        font = pygame.font.Font("data/LiberationSans-Regular.ttf", 15)

        ts = digifont.render("F1 FOR HELP", True, [255, 0, 0])
        self.screen.blit(ts, (sx, 50))

        ts = font.render("Bet:", True, [230, 255, 255])
        self.screen.blit(ts, (sx, 185))
        ts = digifont.render(str(self.bet), True, [255, 0, 0])
        self.screen.blit(ts, (sx, 210))

        ts = font.render("Winner Paid:", True, [230, 255, 255])
        self.screen.blit(ts, (sx, 255))
        ts = digifont.render(str(self.lastwin), True, [255, 0, 0])
        self.screen.blit(ts, (sx, 280))

        ts = font.render("Credit:", True, [230, 255, 255])
        self.screen.blit(ts, (sx, 325))
        ts = digifont.render(str(self.credit), True, [255, 0, 0])
        self.screen.blit(ts, (sx, 350))

    def drawl(self):
        for idx in range(self.npos):
            col = idx // NUM_ROWS
            row = idx % NUM_ROWS
            img = self.raw_imgs[int(self.show[idx]) - 1]
            self.screen.blit(img, (self.col_x(col), self.row_y(row)))

    def randi(self):
        self.showold = []
        if len(self.show) > 1:
            self.showold = list(self.show)
        else:
            self.showold = ["8"] * self.npos
        self.mut = 1
        self.show = []
        for _ in range(self.npos):
            r = randrange(1, 335)
            if r <= 5:
                self.show.append("8")
            elif r <= 15:
                self.show.append("7")
            elif r <= 30:
                self.show.append("6")
            elif r <= 50:
                self.show.append("5")
            elif r <= 120:
                self.show.append("4")
            elif r <= 180:
                self.show.append("3")
            elif r <= 253:
                self.show.append("2")
            else:
                self.show.append("1")

    def check(self):
        self.wins = [0] * NUM_WIN_LINES
        for li, line in enumerate(WIN_LINES):
            if self.show[line[0]] == self.show[line[1]] == self.show[line[2]]:
                c0, r0 = line[0] // NUM_ROWS, line[0] % NUM_ROWS
                c2, r2 = line[2] // NUM_ROWS, line[2] % NUM_ROWS
                x1 = self.col_x(c0) + SYMB_W // 2
                y1 = self.row_y(r0) + SYMB_H // 2
                x2 = self.col_x(c2) + SYMB_W // 2
                y2 = self.row_y(r2) + SYMB_H // 2
                pygame.draw.line(self.screen, [246, 226, 0], (x1, y1), (x2, y2), 6)
                self.wins[li] = int(self.show[line[0]])

    def winner(self):
        self.lastwin = 0
        for n in self.wins:
            if n > 0:
                winsum = self.bet * n + self.bet
                self.credit = self.credit + winsum
                self.lastwin = self.lastwin + winsum
                self.beepsound.play()

    def helpmenu(self):
        pygame.draw.line(self.screen, [176, 176, 176], (50, 250), (590, 250), 400)
        font = pygame.font.Font("data/LiberationSans-Regular.ttf", 15)
        self.screen.blit(font.render("How to play:", True, [255, 255, 255]), (60, 60))
        self.screen.blit(font.render("New spin: left arrow", True, [255, 255, 255]), (60, 80))
        self.screen.blit(font.render("Raise bet: arrow up", True, [255, 255, 255]), (60, 100))
        self.screen.blit(font.render("To end game to high score press Enter", True, [255, 255, 255]), (60, 120))
        self.screen.blit(font.render("To close this as game over help press F1", True, [255, 255, 255]), (60, 160))

    def endthegame(self, scr):
        scrb = int(scr)
        pygame.draw.line(self.screen, [176, 176, 176], (50, 250), (590, 250), 400)
        font = pygame.font.Font("data/LiberationSans-Regular.ttf", 15)
        if self.credit > scrb:
            font = pygame.font.Font("data/LiberationSans-Regular.ttf", 15)
            text_surface = font.render("You have a new high score!!!", True, [255, 255, 255])
            self.screen.blit(text_surface, (60, 60))
            text_surface = font.render("Old high score: "+scr, True, [255, 255, 255])
            self.screen.blit(text_surface, (60, 80))
            text_surface = font.render("New high score: "+str(self.credit), True, [255, 255, 255])
            self.screen.blit(text_surface, (60, 100))
            self.writehs(myhsfile)
        else:
            font = pygame.font.Font("data/LiberationSans-Regular.ttf", 15)
            text_surface = font.render("You ended the game, but you don't have a new high score...", True, [255, 255, 255])
            self.screen.blit(text_surface, (60, 60))
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.JOYBUTTONDOWN):
                if event.type == pygame.QUIT:
                    exit()
                self.bgsound.stop()
                plc = Menu()
    
    def writehs(self, myhsfile):
        writef = open(myhsfile, "w")
        writef.write(str(self.credit))
        writef.close()
        

def help():
    print("BFruit help:")
    print("Options:")
    print("-h, --help        display this help message")
    print("-v, --version     display game version")
    print("Contact: nxbalazs@gmail.com")

if __name__ == "__main__":
    try:
        long = ["help", "version"]
        opts = getopt(argv[1:], "hv", long)[0]
    except GetoptError:
        help()
        exit()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            help()
            exit()
        if opt in ("-v", "--version"):
            print("BFruit - version: "+ VERSION)
            exit()
            

    # .settings:
    homedir = os.path.expanduser("~")
    if homedir[0] == "/":
        mydir = homedir+"/.bfruit"
        myhsfile = mydir+"/hs"
    else:
        mydir = homedir+"\\Application Data\\.bfruit"
        myhsfile = mydir+"\\hs"
    if os.path.exists(mydir) == False:
        os.mkdir(mydir)
    if os.path.exists(myhsfile) == False:
        open(myhsfile, "w").close()
    hsf = open(myhsfile, "r+")
    scr = hsf.readline() # high score
    hsf.close()
    if scr == "":
        scr = "1"

    # pygame init, set display
    pygame.init()
    pygame.joystick.init()
    for i in range(pygame.joystick.get_count()):
        j = pygame.joystick.Joystick(i)
        j.init()
    screen = pygame.display.set_mode([SCREEN_W, SCREEN_H], 0, 24)
    pygame.display.set_caption("BFruit")
    pygame.mouse.set_visible(False)
    
    # intro
    border = pygame.image.load("data/intro/border.png").convert()
    point = pygame.image.load("data/intro/point.png").convert()
    sun = pygame.image.load("data/intro/sun.png").convert()
    
    szam = 0
    while szam < 256:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type in (pygame.KEYDOWN, pygame.JOYBUTTONDOWN):
                plc = Menu()
        screen.fill([0, 0, 0])
        border.set_alpha(szam)
        point.set_alpha(szam)
        screen.blit(border, (160, 120))
        screen.blit(point, (185, 150))
        screen.blit(point, (185, 180))
        screen.blit(point, (185, 210))
        screen.blit(point, (185, 240))
        screen.blit(point, (185, 270))
        screen.blit(point, (215, 150))
        screen.blit(point, (215, 180))
        screen.blit(point, (215, 210))
        screen.blit(point, (215, 240))
        screen.blit(point, (215, 270))
        screen.blit(point, (245, 150))
        screen.blit(point, (245, 180))
        screen.blit(point, (245, 210))
        screen.blit(point, (245, 240))
        screen.blit(point, (245, 270))
        screen.blit(point, (275, 150))
        screen.blit(point, (275, 180))
        screen.blit(point, (275, 210))
        screen.blit(point, (275, 240))
        screen.blit(point, (275, 270))
        screen.blit(point, (305, 150))
        screen.blit(point, (305, 180))
        screen.blit(point, (305, 210))
        screen.blit(point, (305, 240))
        screen.blit(point, (305, 270))
        screen.blit(point, (335, 150))
        screen.blit(point, (335, 180))
        screen.blit(point, (335, 210))
        screen.blit(point, (335, 240))
        screen.blit(point, (335, 270))
        screen.blit(point, (365, 150))
        screen.blit(point, (365, 180))
        screen.blit(point, (365, 210))
        screen.blit(point, (365, 240))
        screen.blit(point, (365, 270))
        screen.blit(point, (395, 150))
        screen.blit(point, (395, 180))
        screen.blit(point, (395, 210))
        screen.blit(point, (395, 240))
        screen.blit(point, (395, 270))
        screen.blit(point, (425, 150))
        screen.blit(point, (425, 180))
        screen.blit(point, (425, 210))
        screen.blit(point, (425, 240))
        screen.blit(point, (425, 270))
        szam = szam + 4
        pygame.display.update()
    
    starttime = time.perf_counter()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type in (pygame.KEYDOWN, pygame.JOYBUTTONDOWN):
                plc = Menu()

        screen.blit(border, (160, 120))
        screen.blit(point, (185, 150))
        screen.blit(point, (185, 180))
        screen.blit(point, (185, 210))
        screen.blit(point, (185, 240))
        if time.perf_counter() - starttime < 1:
            screen.blit(point, (185, 270))
        if time.perf_counter() - starttime < 1.2:
            screen.blit(point, (215, 150))
        screen.blit(point, (215, 180))
        if time.perf_counter() - starttime < 1.15:
            screen.blit(point, (215, 210))
        if time.perf_counter() - starttime < 1.2:
            screen.blit(point, (215, 240))
        if time.perf_counter() - starttime < 1.23:
            screen.blit(point, (215, 270))
        if time.perf_counter() - starttime < 1.18:
            screen.blit(point, (245, 150))
        if time.perf_counter() - starttime < 1.2:
            screen.blit(point, (245, 180))
        screen.blit(point, (245, 210))
        if time.perf_counter() - starttime < 1.43:
            screen.blit(point, (245, 240))
        if time.perf_counter() - starttime < 1.5:
            screen.blit(point, (245, 270))
        screen.blit(point, (275, 150))
        screen.blit(point, (275, 180))
        screen.blit(point, (275, 210))
        screen.blit(point, (275, 240))
        if time.perf_counter() - starttime < 1.22:
            screen.blit(point, (275, 270))
        if time.perf_counter() - starttime < 1.41:
            screen.blit(point, (305, 150))
        if time.perf_counter() - starttime < 1.34:
            screen.blit(point, (305, 180))
        if time.perf_counter() - starttime < 1.4:
            screen.blit(point, (305, 210))
        if time.perf_counter() - starttime < 1.36:
            screen.blit(point, (305, 240))
        if time.perf_counter() - starttime < 1.1:
            screen.blit(point, (305, 270))
        screen.blit(point, (335, 150))
        screen.blit(point, (335, 180))
        screen.blit(point, (335, 210))
        screen.blit(point, (335, 240))
        screen.blit(point, (335, 270))
        screen.blit(point, (365, 150))
        if time.perf_counter() - starttime < 1.13:
            screen.blit(point, (365, 180))
        screen.blit(point, (365, 210))
        if time.perf_counter() - starttime < 1.4:
            screen.blit(point, (365, 240))
        screen.blit(point, (365, 270))
        screen.blit(point, (395, 150))
        if time.perf_counter() - starttime < 1.31:
            screen.blit(point, (395, 180))
        screen.blit(point, (395, 210))
        if time.perf_counter() - starttime < 1.25:
            screen.blit(point, (395, 240))
        screen.blit(point, (395, 270))
        if time.perf_counter() - starttime < 1.43:
            screen.blit(point, (425, 150))
        screen.blit(point, (425, 180))
        if time.perf_counter() - starttime < 2.0:
            screen.blit(point, (425, 210))
        screen.blit(point, (425, 240))
        if time.perf_counter() - starttime < 2.4:
            screen.blit(point, (425, 270))
            
        if time.perf_counter() - starttime > 3:
            font = pygame.font.Font("data/LiberationSans-Regular.ttf", 25)
            text_surface = font.render("nXBalazs" , True, [255, 255, 255])
            screen.blit(text_surface, (190, 273))
        if time.perf_counter() - starttime > 3.5:
            font = pygame.font.Font("data/LiberationSans-Regular.ttf", 25)
            text_surface = font.render("games" , True, [255, 255, 255])
            screen.blit(text_surface, (280, 310))
        if 5 > time.perf_counter() - starttime > 4:
            szamsun = 0
            while szamsun < 100:
                sun.set_alpha(szamsun)
                screen.blit(sun, (0, 0))
                szamsun = szamsun + 1
                pygame.display.update()
        if time.perf_counter() - starttime > 5:
            plc = Menu()
    
    
    
        pygame.display.update()
