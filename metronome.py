import sounddevice as sd
import numpy as np  # Make sure NumPy is loaded before it is used in the callback
assert np  # avoid "imported but unused" message (W0611)
import queue
import time

tempo = 120
amplitude = 0.2
frequency = 500
samplerate = 44100
num_beats = 12


def create_beat(tempo):
    frequency = 500
    rampupfac = 0
    rampdownfac = 0.3
    beepratio = 0.1
    secperbeat = 1/tempo*60

    t_beep = np.arange(0.0, secperbeat*beepratio, 1/samplerate)

    beep = amplitude * np.sin(2 * np.pi * frequency * t_beep)

    rampup = np.arange(int(len(beep)*rampupfac))
    rampup = rampup/len(rampup)
    rampdown= np.flip(np.arange(int(len(beep))*rampdownfac), axis=0)
    rampdown = rampdown/len(rampdown)
    ones = np.repeat(1, len(beep) - (len(rampup)+len(rampdown)))
    mask = np.append(rampup, ones)
    mask = np.append(mask, rampdown)
    beep = np.multiply(mask, beep)

    beat = np.append(beep, np.zeros(int(secperbeat*(1-beepratio)*samplerate)))
    beat = np.float32(np.transpose(np.tile(beat, (2, 1))))


    return(beat)

def click_on(tempo):
    sd.play(create_beat(tempo), samplerate=None, mapping=None, blocking=False, loop=True)

def click_off():
    sd.stop()

if __name__ == "__main__":
    while True:
        sd.sleep(1000)

