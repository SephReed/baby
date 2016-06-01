#!/usr/bin/python3

import RPi.GPIO as GPIO
from time import sleep
# import simpleaudio as sa
import pygame
from random import randint



#init sounds
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
pygame.mixer.init()

CRY_WAV = pygame.mixer.Sound("sounds/baby_cry.wav")
GIGGLE_WAV = pygame.mixer.Sound("sounds/baby_giggle3.wav")
GIGGLE_WAV.play()





TIME_INCREMENT = 0.001
GPIO_BCM_MAP = [4, 17, 18, 27, 22, 23, 24, 25]
NUM_INPUTS = 8
input_states = [0] * NUM_INPUTS
input_timeouts = [0] * NUM_INPUTS


time_untouched = 0
time_till_cry = 3200
# time_till_cry = 15
# time_since_key_change = 0
# time_for_key_change = 10

baby_crying = 0





GPIO.setmode(GPIO.BCM)
# GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("GPIO Set up")



# MAJOR_SCALE = [0, 2, 4,  7, 9, 11]
# HARM_MINOR_CHORD = [0, 3, 7, 11]
# PENTATONIC_SCALE = [0, 2, 4, 7, 9]
# HARM_MINOR_SCALE = [0, 2, 3, 6, 7, 8, 11]



SCALES = [
    [                       #MAJOR SCALE
        [0, 2, 4, 7, 9],    #PENTATONIC
        [0, 4, 7, 11],      #ROOT MAJOR 7th
        [9, 0, 4, 7],       #ROOT MINOR 7th
        [0, 4, 7],          #ROOT MAJOR 5th
        [9, 0, 4],          #ROOT MINOR 5th
        [2, 7, 11],         #5th
        [2, 5, 9],          #2nd
        [0, 5, 9],          #4th
    ],

    [                       #HARMONIC_MINOR
        # [0, 3, 7, 11],      #ROOT HMINOR 7th
        # [0, 3, 7],          #ROOT HMINOR 5th
        # [8, 0, 3, 7],       #Extended 6th
        # [3, 7, 11],         #5th
        # [5, 8, 11, 0],      #4th
        [6, 0, 4, 8],       #ROOT HMINOR 7th
        [6, 0, 4],          #ROOT HMINOR 5th
        [5, 9, 0, 4],       #Extended 6th
        [4, 8, 0, 2],          #Augmented 5th
        [2, 5, 8, 0],       #Half-Dimished 4th
    ],
]


TIME_SINCE_ROOT_TRANSPOSE = 0
TIME_SINCE_SCALE_CHANGE = 0
TIME_SINCE_SUBSCALE_CHANGE = 0


INTERVAL_ROOT_TRANSPOSE = 15
INTERVAL_SCALE_CHANGE = 25
INTERVAL_SUBSCALE_CHANGE = 5


ROOT = 0
SCALE = 0
SUBSCALE = 0


def stepKeyChange():
    global ROOT
    global SCALE
    global SUBSCALE

    global TIME_SINCE_ROOT_TRANSPOSE
    global TIME_SINCE_SCALE_CHANGE
    global TIME_SINCE_SUBSCALE_CHANGE


    keyChanged = 0
    TIME_SINCE_ROOT_TRANSPOSE += TIME_INCREMENT
    TIME_SINCE_SCALE_CHANGE += TIME_INCREMENT
    TIME_SINCE_SUBSCALE_CHANGE += TIME_INCREMENT


    if TIME_SINCE_ROOT_TRANSPOSE > INTERVAL_ROOT_TRANSPOSE:
        TIME_SINCE_ROOT_TRANSPOSE = 0
        keyChanged = 1 

        guess = randint(1,7)
        transpose = 0
        if guess <= 4:
            transpose = 5
        elif guess <= 6:
            transpose = 7
        else:
            transpose = -4

        SUBSCALE = 0

        print("transposing "+str(transpose))

        ROOT += transpose
        ROOT += 12
        ROOT %= 12


    if TIME_SINCE_SCALE_CHANGE > INTERVAL_SCALE_CHANGE:
        keyChanged = 1 
        TIME_SINCE_SCALE_CHANGE = 0
        SCALE = randint(0, len(SCALES)-1)
        SUBSCALE = 0
        print("scale changed "+str(SCALE))

    if TIME_SINCE_SUBSCALE_CHANGE > INTERVAL_SUBSCALE_CHANGE:
        keyChanged = 1 
        TIME_SINCE_SUBSCALE_CHANGE = 0
        SUBSCALE = randint(0, len(SCALES[SCALE])-1)
        print("subscale changed "+str(SUBSCALE))

    if keyChanged == 1:
        updateKeys()


IN_KEY = []
BUTTON_NOTES = []
def updateKeys():
    global IN_KEY
    global BUTTON_NOTES
    IN_KEY = []
    subscale = SCALES[SCALE][SUBSCALE]

    for octave in range(3):
        for interval in subscale:
            IN_KEY += [(octave*12)+((ROOT+interval)%12)]

    IN_KEY.sort()

    BUTTON_NOTES = []
    for btn in range(NUM_INPUTS):
        randInKey = -1
        while randInKey == -1 or randInKey in BUTTON_NOTES:
            randInKey = IN_KEY[randint(0, len(IN_KEY)-1)]    
        
        BUTTON_NOTES += [randInKey]

    BUTTON_NOTES.sort()
    print(str(BUTTON_NOTES))


updateKeys()





KEY_NAMES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
MUSIC_BOX_WAVS = [None] * (36)

soundNum = 0
for i in range(3):
    for key in KEY_NAMES:
        filename = "sounds/musicbox/" + str(i+1) + key + ".wav"
        print(filename + " index " +str(soundNum))
        MUSIC_BOX_WAVS[soundNum] = pygame.mixer.Sound(filename)
        soundNum += 1



TEST_MODE = 0

def stepGPIO():
    for i in range(NUM_INPUTS):
        if TEST_MODE == 1 and randint(1, 150) == 1:
            buttonPress(i)

        if input_timeouts[i] > 0:
            input_timeouts[i] -= TIME_INCREMENT

        stateNow = GPIO.input(GPIO_BCM_MAP[i])

        if stateNow != input_states[i]:
            input_states[i] = stateNow

            if stateNow == 0:
                buttonPress(i)



num_touches = -1
def buttonPress(buttonNum):
    global time_untouched
    global QUEUED_NOTES
    global num_touches

    if input_timeouts[buttonNum] <= 0:

        if num_touches != -1:
            num_touches += 1
            if num_touches >= 10:
                GIGGLE_WAV.play()
                time_untouched = 0
                num_touches = -1

        if time_untouched > 900: #900
            if num_touches == -1:
                num_touches = 0
            # time_untouched -= 300
            time_untouched -= 5

        else:
            time_untouched = 0

        input_timeouts[buttonNum] = 0.14
        print("button press "+str(buttonNum))
        # randSound = IN_KEY[randint(0, len(IN_KEY)-1)]
        # QUEUED_SOUNDS += [BUTTON_NOTES[i]]
        QUEUED_NOTES += [BUTTON_NOTES[buttonNum]]




def stepCry():
    global baby_crying
    global time_untouched

    if baby_crying == 0:
        time_untouched += TIME_INCREMENT

    if time_untouched > time_till_cry and baby_crying == 0:
        baby_crying = 1
        print("cry on")
        CRY_WAV.play(loops=-1)

    elif time_untouched <= time_till_cry and baby_crying == 1:
        baby_crying = 0
        print("cry off")
        CRY_WAV.fadeout(1000)
        



# QUEUED_SOUNDS = []
QUEUED_NOTES = []
QUANTIZE = 0.15
time_since_quant = 0

def stepReleaseHeld():
    global time_since_quant
    global QUEUED_NOTES
    time_since_quant += TIME_INCREMENT

    if time_since_quant > QUANTIZE:
        time_since_quant = 0
        for note in QUEUED_NOTES:
            MUSIC_BOX_WAVS[note].play()

        QUEUED_NOTES = []







for chan in GPIO_BCM_MAP:
    GPIO.setup(chan, GPIO.IN, pull_up_down=GPIO.PUD_UP)



while 1:
    stepGPIO()
    stepCry()
    stepKeyChange()
    stepReleaseHeld()
    sleep(TIME_INCREMENT)
    
                

