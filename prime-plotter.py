import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import pyaudio
import argparse

## TODO: Cleanup this part
# Parameters to tune
NOTE_VOLUME = 0.5     # range [0.0, 1.0]
NOTE_DURATION = 0.4   # in seconds, may be float
NOTE_BASE_FREQUENCY = 190
GRAPH_ANIMATION_INTERVAL = 20

SOUND_FLAG = False
p = 0
audio_stream = 0
sample_rate = 44100       # sampling rate, Hz, must be integer

xs = []
ys = []

style.use('fivethirtyeight')
fig = plt.figure(figsize=(15, 8))
ax1 = fig.add_subplot(1,1,1)

previous_prime = 1
previous_max_gap = 1
prime_gap = 1

def refresh_graph():
    # Setup graph colors and text
    ax1.clear()
    plt.grid(color='dimgrey')
    fig.patch.set_facecolor('black')
    ax1.spines['bottom'].set_color('white')
    ax1.spines['top'].set_color('white')
    ax1.xaxis.label.set_color('white')
    ax1.yaxis.label.set_color('white')
    ax1.set_facecolor('xkcd:navy')
    ax1.tick_params(axis='x', colors='white')
    ax1.tick_params(axis='y', colors='white')
    plt.xlabel('Number')
    ## TODO: Change Y label based on mode
    plt.ylabel('Gap with previous prime')
    title_string = f'Prime: {previous_prime or "-"}, Gap note: {prime_gap or "-"} x {NOTE_BASE_FREQUENCY} Hz'
    ax1.set_title(title_string, c = 'white')
#    ax1.plot(xs, ys, c = 'orange', linewidth=0.75)
    ax1.bar(xs, ys, color = 'orange', width=0.2)
#    ax1.bar(xs, ys, color = 'orange')
#    ax1.set_xbound(-1.0, 50)
    #ax1.scatter(xs, ys, c = 'lime', s=2)

def play_note(note):
    samples = (np.sin(2*np.pi*np.arange(sample_rate*NOTE_DURATION)*note*NOTE_BASE_FREQUENCY/sample_rate)).astype(np.float32)
    audio_stream.write(NOTE_VOLUME*samples)

def is_prime(i):
    if i <= 1:
        return False

    for k in range(2, i):
        if (i % k) == 0:
            return False
    return True


def core_function(i, mode):
    global previous_prime
    global prime_gap
    global previous_max_gap

    if is_prime(i):
        prime_gap = i - previous_prime # Delta between consecutive primes
        if mode == 'prime-gap':
            y = prime_gap
            xs.append(float(i))
            ys.append(float(y))
        elif 'maxgap' in mode:
            y = 1
            if prime_gap > previous_max_gap:
                #this prime_gap is max so far
                print(f'i: {i} prime gap: {prime_gap}, new max gap. previous_max_gap: {previous_max_gap}')
                if mode == 'maxgaps':
                    y = prime_gap # Just the max gap value
                if mode == 'gap-of-maxgaps':
                    y = prime_gap - previous_max_gap # Delta of max gap to max gap (y)
                if mode == 'ratio-of-maxgaps':
                    y = prime_gap / previous_max_gap # ratio of max gap to max gap (y)
                if mode == 'ratio-of-primes-at-maxgaps':
                    y = i / previous_prime # ratio of prime to prime(x) who are max gaps
                if mode == 'ratio-of-maxgap-to-interval':
                    y = prime_gap / i
                xs.append(float(i))
                ys.append(float(y))

                #y = i % previous_prime
                #y = prime_gap - previous_max_gap # Delta of max gap to max gap (y)
                print(f'Y is {y}')
                previous_max_gap = prime_gap
        #xs.append(float(i))
        #ys.append(float(y))
        print(f'i: {i} prime gap: {prime_gap}, previous_prime: {previous_prime}')
        if SOUND_FLAG:
            play_note(y)
        previous_prime = i

def plot_with_mode(i, mode, limit, animate_flag):

    if animate_flag:
        if i >= limit:
            return
        core_function(i, mode)
    else:
        for i in range(2, limit):
            core_function(i, mode)

    refresh_graph()

def init_sound():
    global p
    global audio_stream
    p = pyaudio.PyAudio()

    audio_stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    output=True)
def close_sound():
    audio_stream.close()
    p.terminate()

def main():
    global SOUND_FLAG

    parser = argparse.ArgumentParser(description='prime-plotter.py: A script to represent some properties of prime numbers visually and audibly')

    mode_choices = ['prime-gap', 'maxgaps', 'gap-of-maxgaps', 'ratio-of-maxgaps', 'ratio-of-primes-at-maxgaps', 'ratio-of-maxgap-to-interval']

    parser.add_argument('-m','--mode', choices=mode_choices, help='What should the script plot?', default = 'prime-gap', metavar = '')
    parser.add_argument('-l','--limit', help='Number upper limit', default = 100, type = int, metavar = '')
    parser.add_argument('-a','--animate', help='Animate flag', action ='store_true')
    parser.add_argument('-s','--sound', help='Play musical notes representing values', action ='store_true')

    args = vars(parser.parse_args())

    mode = args['mode']
    limit = args['limit']
    animate_flag = args['animate']
    SOUND_FLAG = args['sound']
    print(f'Running in [{mode}] mode with [{limit}] as the upper limit. Animation: [{"ON" if animate_flag else "OFF"}], Sound: [{"ON" if SOUND_FLAG else "OFF"}]')
    refresh_graph()
    if SOUND_FLAG:
        print('Musical notes turned on')
        init_sound()

    if animate_flag:
        ani = animation.FuncAnimation(fig, plot_with_mode, interval=GRAPH_ANIMATION_INTERVAL, fargs=(mode,limit,animate_flag))
        plt.show()
    else:
        #pass
        plot_with_mode('', mode, limit, animate_flag)
        plt.show()

    if SOUND_FLAG:
        close_sound()


if __name__ == "__main__":
    main()
