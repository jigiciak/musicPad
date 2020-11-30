import pygame as pg
from easygui import fileopenbox
import rtmidi
from time import time
import numpy as np

class Pad(pg.rect.Rect):
    def __init__(self, screen, top, left, width, height, midiPad, sound_channel):
        super().__init__(top, left, width, height)
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        self.data = None
        self.screen = screen
        self.midiPad = midiPad
        self.sound_channel = pg.mixer.Channel(sound_channel)
        pg.draw.rect(screen, (170, 170, 170), [self.top, self.left, self.width, self. height])

    def update(self, pos, message):
        if self.top <= pos[0] <= self.top + self.width and self.left <= pos[1] <= self.left + self.height:
            pg.draw.rect(self.screen, (100, 100, 100), [self.top, self.left, self.width, self. height])
        elif message[2] != 0:
            if message[1] == self.midiPad:
                pg.draw.rect(self.screen, (100, 100, 100), [self.top, self.left, self.width, self.height])
        else:
            pg.draw.rect(self.screen, (160, 160, 160), [self.top, self.left, self.width, self. height])


class LoadPad(pg.rect.Rect):
    def __init__(self, screen, top, left, width, height):
        super().__init__(top, left, width, height)
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        self.screen = screen
        pg.draw.rect(screen, (255, 255, 255), [self.top, self.left, self.width, self. height])

    def update(self, pos):
        if self.top <= pos[0] <= self.top + self.width and self.left <= pos[1] <= self.left + self.height:
            pg.draw.rect(self.screen, (150, 150, 150), [self.top, self.left, self.width, self. height])
        else:
            pg.draw.rect(self.screen, (200, 200, 200), [self.top, self.left, self.width, self. height])


class LoopTile(pg.rect.Rect):
    def __init__(self, screen, top, left, size, pad_id, loop_id):
        super().__init__(top, left, size, size)
        self.top = top
        self.left = left
        self.width = size
        self.height = size
        self.screen = screen
        self.pad_id = pad_id
        self.loop_id = loop_id
        self.active = False
        pg.draw.rect(screen, (100, 100, 100), [self.top, self.left, self.width, self.height])

    def update(self, loop_id):
        # if self.top <= pos[0] <= self.top + self.width and self.left <= pos[1] <= self.left + self.height:
        #     pg.draw.rect(self.screen, (150, 150, 150), [self.top, self.left, self.width, self.height])
        # else:
        #     pg.draw.rect(self.screen, (200, 200, 200), [self.top, self.left, self.width, self.height])
        if loop_id == self.loop_id:
            pg.draw.rect(self.screen, (200, 200, 200), [self.top, self.left, self.width, self.height])
            if self.active:
                pg.mixer.Sound('sounds/Hat_Closed_1.wav').play()
        else:
            pg.draw.rect(self.screen, (100, 100, 100), [self.top, self.left, self.width, self.height])


def buttons_update(buttons, loads, pos, message):
    for i, button in enumerate(buttons):
        button.update(pos, message)
        loads[i].update(pos)


def buttons_events(buttons, loads, pos, message):
    for i, button in enumerate(buttons):
        if button.top <= pos[0] <= button.top + button.width and button.left <= pos[1] <= button.left + button.width:
            if not loads[i].top <= pos[0] <= loads[i].top + loads[i].width and not loads[i].left <= pos[1] <= loads[i].left + loads[i].width:
                if button.data:
                    if not button.sound_channel.get_busy():
                        button.sound_channel.play(button.data)
                    else:
                        button.sound_channel.fadeout(25)
                        button.sound_channel.play(button.data)
                    buttons_update(buttons, loads, pos, message)

        if loads[i].top <= pos[0] <= loads[i].top + loads[i].width and loads[i].left <= pos[1] <= loads[i].left + loads[i].width:
            button.data = pg.mixer.Sound(fileopenbox())


def pads_events(buttons, message):
    for i, button in enumerate(buttons):
        if message[1] == button.midiPad and message[2] != 0:
            if button.data:
                if not button.sound_channel.get_busy():
                    button.sound_channel.play(button.data)
                else:
                    button.sound_channel.fadeout(25)
                    button.sound_channel.play(button.data)


def loop_update(loop_bt, loop_id):
    for i in range(4):
        for j in range(16):
            loop_bt[i, j].update(loop_id)

def init_GUI():
    pg.mixer.pre_init(44100, -16, 5, 512)
    pg.init()
    res = (650, 540)
    screen = pg.display.set_mode(res)
    screen.fill((60, 25, 60))

    spacing = 10
    size_pad = 150
    size_load = 30
    channel = 0
    buttons = [Pad(screen,
                   spacing * i + size_pad * (i-1),
                   spacing,
                   size_pad,
                   size_pad, 35 + i, channel + i)
               for i in range(1, 5)]

    loads = [LoadPad(screen,
                     spacing * i + size_pad * i - size_load - 5,
                     size_pad + spacing - size_load + 10,
                     size_load,
                     size_load - 15)
             for i in range(1, 5)]

    loop_bt = np.empty((4, 16), dtype=object)
    for i in range(4):
        for j in range(16):
            loop_bt[i, j] = LoopTile(screen, spacing * (j + 1) + 10 * j, screen.get_height() - 10 * (i+1) - spacing * (i+1), 10, i, j)
    print(loop_bt)
    return screen, buttons, loads, loop_bt


def midi_event(message):
    PADEVENT = pg.event.Event(pg.USEREVENT, {'stock': 0, 'id': 0, 'value': 0})
    if message[1] == 36 and message[2] != 0:
        PADEVENT = pg.event.Event(pg.USEREVENT + 1, {'stock': 144, 'id': 36, 'value': message[2]})
    elif message[1] == 37 and message[2] != 0:
        PADEVENT = pg.event.Event(pg.USEREVENT + 2, {'stock': 144, 'id': 37, 'value': message[2]})
    elif message[1] == 38 and message[2] != 0:
        PADEVENT = pg.event.Event(pg.USEREVENT + 3, {'stock': 144, 'id': 38, 'value': message[2]})
    elif message[1] == 39 and message[2] != 0:
        PADEVENT = pg.event.Event(pg.USEREVENT + 4, {'stock': 144, 'id': 39, 'value': message[2]})
    return PADEVENT


def main():
    screen, buttons, loads, loop_bt = init_GUI()
    midiIn = rtmidi.MidiIn()
    midiIn.open_port(0)
    message = [0, 0, 0]
    #
    BPM = 60
    DELTA = 60000//BPM
    LOOPEVENT = pg.time.set_timer(pg.USEREVENT + 5, DELTA//4)

    sound = pg.mixer.Sound("sounds/Hat_Closed_1.wav")
    loop_ct = 0
    while True:
        read = midiIn.get_message()
        if read:
            message = read[0]
            pg.event.post(midi_event(message))
        mouse = pg.mouse.get_pos()
        for ev in pg.event.get():
            if ev.type == pg.USEREVENT + 5:
                loop_update(loop_bt, loop_ct)
                if loop_ct == 15:
                    loop_ct = 0
                else:
                    loop_ct += 1

            if ev.type == pg.QUIT:
                pg.quit()
            if ev.type == pg.MOUSEBUTTONDOWN:
                buttons_events(buttons, loads, mouse, message)
            if ev.type == pg.USEREVENT + 1:
                pads_events(buttons, message)
            if ev.type == pg.USEREVENT + 2:
                pads_events(buttons, message)
            if ev.type == pg.USEREVENT + 3:
                pads_events(buttons, message)
            if ev.type == pg.USEREVENT + 4:
                pads_events(buttons, message)
        buttons_update(buttons, loads, mouse, message)
        pg.display.update()


if __name__ == "__main__":
    main()
