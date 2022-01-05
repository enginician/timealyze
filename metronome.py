import sounddevice as sd
import numpy as np  # Make sure NumPy is loaded before it is used in the callback
assert np  # avoid "imported but unused" message (W0611)
import time
import matplotlib.pyplot as plt
#
tempo = 120
amplitude = 0.2
frequency = 500
samplerate = 44100
rampupfac = 0
rampdownfac = 0.3
beepratio = 0.1
num_beats = 12
secperbeat = 1/tempo*60

# create a function that creates a single metronome beep. By calling this function multiple times, a whole bar and multiple bars are going to be created

def create_beat(tempo, frequency, rampupfac, rampdownfac, beepratio, secperbeat):


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

       return(beat)

audio = np.empty(0)
t = np.empty(0)

for i in range(num_beats):
       beat = create_beat(tempo, frequency, rampupfac, rampdownfac, beepratio, secperbeat)
       audio = np.append(audio, beat)

sd.play(audio)

t = np.arange(0.0, secperbeat * num_beats, 1/samplerate)

print(len(audio))
print(len(t))

fig, ax = plt.subplots()
ax.plot(t, audio)

ax.set(xlabel='time (s)', ylabel='voltage (mV)',
       title='About as simple as it gets, folks')
ax.grid()

plt.show()