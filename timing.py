import matplotlib.pyplot as plt
import numpy as np
import wave
import sys
import statistics

########################################
#           INPUT PARAMETER            #
########################################
bpm = 136
offsetms = 0  # offset for beat grid in ms. Moves the beat grid to the right and is used to align with recording. Set to 0 to have program search for correct offset!
threshold = 5000  # signal threshold that needs to be exceeded to detect a note
deadzone = 0  # deadzone in per cent of subdivision. Beats within the value's percentage are ignored at the beinning and the end of a grid boundary
subdiv = 4  # 1 for quarter notes, 2 for eights, 3 for triplets and so on
cappeaks = True  # This can be helpful if the waveform of some sounds has its max value further in the back and not just at the beginning of the onset.
sigma16threshold = 1  # threshold standard deviation for offset finding algorithm in 16th notes
muthreshold = 0.6  # threshold for offset finding algorithm in ms

########################################

def timealyze(bpm, offsetms, threshold, deadzone, subdiv, cappeaks):

    file = "output.wav"

    spf = wave.open(file, "r")

    # Extract Raw Audio from Wav File
    signal = spf.readframes(-1)
    signal = np.frombuffer(signal, "Int16")
    fs = spf.getframerate()

    # If Stereo
    if spf.getnchannels() == 2:
        print("Just mono files")
        sys.exit(0)


    time = np.linspace(0, len(signal) / fs, num=len(signal))

    # normalize signal (didn't work properly, only looked at positive peaks)
    maxvalue = np.argmax(signal)
    minvalue = np.argmin(signal)
    signal = signal / signal[maxvalue] * 2**16 *0.5 #set factor to 0.5 for clean normalization.

    # cap peaks
    if cappeaks == True:
        signal[signal > (signal[maxvalue]*0.7)] = signal[maxvalue]*0.7

    deadzonems = deadzone * 60 / bpm / subdiv / 100 *1000 # deadzone in ms after and before grid boundary in which a beat cannot be detected. Prevents beat detection through maximum value at beginning of grid due to crash cymbal noise from beat before
    offset = int(offsetms*fs/1000) #offset for beat grid in samples. Used for internal calculations below
    deadzone = (deadzonems*fs/1000)
    gw = int(fs*60/bpm/subdiv)
    #initialize mu and sigma 16
    mu = -1
    sigma16 = 1

    def analyze(offset, mu):
        beatindex = []
        gridindex = []
        targetindex = []
        targetdiff = []
        xlate = []
        xearly = []
        targetdiff16 = []
        targetdiffms = []
        deadzonefill = []
        # test out peak finding and filtering
        #peaks, _ = find_peaks(signal, height = 5000, prominence = 5000, distance = 1000)

        # filter signal
        #signal = savgol_filter(signal, 51, 3) # window size 51, polynomial order 3

        # apply time grid (based on click tempo and sub division) on wave signal, identify beats and compare to perfectly timed beat
        for i in range(int(len(signal)/gw-(offset/gw))):
            signalfreg = signal[(gw*(i)+offset):(gw*(i+1)+offset)] # create signal fregment from wave signal according to time grid
            gridindex.append((gw*i+offset)/fs) # create list with grid boundaries to plot grid
            deadzonefill.append(np.arange(gridindex[i]-deadzonems/1000, gridindex[i]+deadzonems/1000, 0.001))

            maxvalue = np.argmax(signalfreg)

            if signalfreg[maxvalue] > threshold and ((maxvalue-gridindex[-1]) > deadzone and (gridindex[-1] + gw - maxvalue) > deadzone  ): # if statement to prevent peaks in signal noise to be recognized as beats in grid segements without notes
                beatindex.append((maxvalue+(gw*i)+offset)/fs) # add index value of recognized beat (converted to seconds)
                targetindex.append((gw *i+offset+int(gw/2))/fs) # add index value for perfectly timed beat for comparison#
                # fill lists with x values to color fill the area between the perfectly timed and actual beats (late and early seperated to have different colors)
                targetdiff.append(beatindex[-1]-targetindex[-1])
                if targetdiff[-1] <= 0:
                    xearly.append(np.arange(beatindex[-1], targetindex[-1], 0.001))
                if targetdiff[-1] > 0:
                    xlate.append(np.arange(targetindex[-1], beatindex[-1], 0.001))

        # convert peaks for time in seconds
        ##peakssec = []
        ##for i in range(len(peaks)):
        ##    peakssec.append(peaks[i]/fs)
        ##
        ##ax1.plot(peakssec, signal[peaks], "x")

        # convert targetdiff to percentage of 16th notes
        for i in range(len(targetdiff)):
            targetdiff16.append(targetdiff[i]* bpm/60*4)

        # convert targetdiff to milli seconds
        for i in range(len(targetdiff)):
            targetdiffms.append(targetdiff[i] * 1000)

        sigma16 = statistics.stdev(targetdiff16)
        mu = statistics.mean(targetdiffms)

        return offset, mu, sigma16, beatindex, gridindex, targetindex, xlate, xearly, targetdiff16, targetdiffms, deadzonefill

    ###########################################################################################################################

    if offsetms == 0:

        # create loop to fit offset such that the mean deviation is minimized (the analysis focusses on relative timing rather than absolute timing because there is no absolute timing reference available (e.g. a click))
        # simple and ugly brute force while loop without exit condition, fix later
        while abs(mu) > muthreshold or sigma16 > sigma16threshold :
            try:
                offset = int(offsetms*fs/1000) #offset for geat grid in samples. Used for internal calculations below

                offset, mu, sigma16, beatindex, gridindex, targetindex, xlate, xearly, targetdiff16, targetdiffms, deadzonefill = analyze(offset, mu)

                if abs(mu) > 10:
                    offsetms +=10
                else:
                    offsetms += 1
                print("the offset is {} ms, mu is {} ms and sigma16 is {}".format(round(offsetms,1), round(mu, 2),round(sigma16,2)))
            except:
                offsetms += 100
                continue

        offsetms -=1

    ###############################################################################################################################


    #########################
    offset, mu, sigma16, beatindex, gridindex, targetindex, xlate, xearly, targetdiff16, targetdiffms, deadzonefill = analyze(offset, mu)
    #########################



    print("\n")
    print("The offset was set to {} ms".format(offsetms))
    print("\n")
    print ("Im Durchschnitt liegst du {} 16tel neben dem Beat".format(round(sigma16,2)))
    print ("Das sind etwa {} ms".format(round(sigma16/4/bpm*60*1000,2)))
    print ("\n")
    print("Insgesamt wurden {} Schläge detektiert".format(len(beatindex)))
    print ("Die Durchschnitssabweichung liegt bei {} ms. Passe den Offset an, um diesen Wert so nahe wie möglich gegen 0 einzustellen".format(round(mu)))

    fig = plt.figure(figsize=(16,9))
    ax1 = fig.add_subplot(311)
    ax1.set_ylabel('Signallevel')
    ax1.set_title("timealyze - Timinganalyse")

    ax1.plot(time,signal)

    ax2 = fig.add_subplot(312,sharex = ax1)
    ax2.set_xlabel('Zeit [s]')

    ax1.hlines(threshold, 0, max(time), colors='gray', linestyles='dotted', label='Threshold', linewidth = 0.2)
    for i in range(len(gridindex)):
        ax1.axvline(x=gridindex[i], color = "gray", linestyle = 'dotted', linewidth = 0.6)
        ax2.axvline(x=gridindex[i], color = "darkgray", linestyle = 'dotted', linewidth = 0.6)
    for i in range(len(beatindex)):
        ax1.axvline(x=beatindex[i], color = "orange", linewidth = 0.5)
        ax2.axvline(x=beatindex[i], color = "black", linewidth = 0.8)
    for i in range(len(targetindex)):
        ax2.axvline(targetindex[i], color = "dimgray", linewidth = 0.8)
    for i in range (len(xlate)):
        ax2.fill_between(xlate[i], 10, -10, facecolor ='red')
    for i in range (len(xearly)):
        ax2.fill_between(xearly[i], 10, -10, facecolor ='orangered')

    for i in range(len(deadzonefill)):
        ax1.fill_between(deadzonefill[i], -2**16, 2**16, facecolor ='lightgray', alpha = 0.5)

    ax1.set_ylim([-2**16/2, 2**16/2])
    ax2.set_ylim([0,1])

    mu16 = statistics.mean(targetdiff16)
    mums = statistics.mean(targetdiffms)
    sigmams = statistics.stdev(targetdiffms)
    num_bins = 20

    ax3 = fig.add_subplot(337)
    n, bins, patches = ax3.hist(targetdiffms, num_bins, density=1)
    ax3.set_xlabel("Abweichung vom Sollbeat in ms")
    ax3.set_ylabel("Relative Häufigkeit")
    ax3.grid(color = 'gray', linestyle = 'dotted', linewidth = 0.3)
    y1 = ((1 / (np.sqrt(2 * np.pi) * sigmams)) *
         np.exp(-0.5 * (1 / sigmams * (bins - mums))**2))
    ax3.plot(bins, y1, '--')
    ax3.set_xlim([-1/4*60/bpm*1000,1/4*60/bpm*1000])

    ax4 = fig.add_subplot(338)
    ax4.hist(targetdiff16, num_bins)
    ax4.set_xlabel("Abweichung vom Sollbeat [in 16tel Noten]")
    ax4.set_ylabel("Anzahl detektierte Schläge")
    ax4.grid(color = 'gray', linestyle = 'dotted', linewidth = 0.3)
    ax4.set_xlim([-1,1])

    plt.text(0.68, 0.30, "Durchschnittliche Abweichung vom Beat:".format(round(sigma16/4/bpm*60*1000,2)), fontsize=10, transform=plt.gcf().transFigure)
    plt.text(0.68, 0.26, "                {} ms    ".format(round(sigma16/4/bpm*60*1000,2)), fontsize=14, transform=plt.gcf().transFigure)
    plt.text(0.68, 0.21, "Das entspricht: ".format(round(sigma16/4/bpm*60*1000,2)), fontsize=10, transform=plt.gcf().transFigure)
    plt.text(0.68, 0.17, "         {} 16tel-Noten    ".format(round(sigma16,2)), fontsize=14, transform=plt.gcf().transFigure)

    plt.text(0.68, 0.11, "Verwendete Parametereinstellungen:", fontsize=6, transform=plt.gcf().transFigure)
    plt.text(0.68, 0.09, "[BPM: {}], [Offset: {} ms], [Threshold: {}], [Subdiv: {}]".format(bpm, offsetms, threshold, subdiv), fontsize=6, transform=plt.gcf().transFigure)
    plt.text(0.68, 0.075, "[CapPeaks: {}], [Sigma16Threshold: {}], [MuThreshold: {}]".format(cappeaks, sigma16threshold, muthreshold), fontsize=6, transform=plt.gcf().transFigure)

    plt.text(0.95, 0.02, "v1.0.0", fontsize=6, transform=plt.gcf().transFigure)

    #plt.tight_layout()

    # Return value to show score in GUI
    return sigmams, len(beatindex)

def showplot():
    plt.show()

if __name__ == '__main__':

    timealyze(bpm, offsetms, threshold, deadzone, subdiv, cappeaks)
    showplot()
