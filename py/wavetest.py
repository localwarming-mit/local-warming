import curses, math, time, traceback
from curses import wrapper

amplitude = 2

#stdscr = curses.initscr()
current_milli_time = lambda: time.time()

def wavePtAt(t, amplitude, offset):
    return amplitude*math.sin(t+offset)


def nextN(t, n=10, phase=1.5):
    global amplitude
    vals = []
    for i in range(n):
        vals.append(wavePtAt(t, amplitude, (phase*i)))
    return vals

#screen = None
def curses_main(stdscr):
    # Frame the interface area at fixed VT100 size
    #global screen
    #screen = stdscr.subwin(7, 12, 30, 12)
    stdscr.resize(7, 12)
    #stdscr.mvwin(30, 12)
    stdscr.box()
    stdscr.refresh();
    stdscr.addstr(1, 1, "hello")
    stdscr.addstr(2, 1, "world")

    while(True):
        t = current_milli_time()
        dat = nextN(t)
        lines = printWave(dat)
        i = 1
        for line in lines:
            stdscr.addstr(i, 1, line)
            i = i + 1
        stdscr.refresh()
        #stdscr.getkey()

    # Define the topbar menus
    # file_menu = ("File", "file_func()")
    # proxy_menu = ("Proxy Mode", "proxy_func()")
    # doit_menu = ("Do It!", "doit_func()")
    # help_menu = ("Help", "help_func()")
    # exit_menu = ("Exit", "EXIT")
    # # Add the topbar menus to screen object
    # topbar_menu((file_menu, proxy_menu, doit_menu,
    #              help_menu, exit_menu))
    # # Enter the topbar menu loop
    # while topbar_key_handler():
    #     draw_dict()


def printWave(arr, amplitude=2):
    lines = []
    arr2 = map(int, map(round, arr))
    #print arr2
    amplitude_i = amplitude
    while(amplitude_i >= -amplitude):
        s= ""
        indices = [i for i, x in enumerate(arr2) if x == amplitude_i]
        #print indices
        if len(indices) > 0:
            ind = indices[0]
            s = s + (" "*ind) + "*"
            i = 1
            while i < len(indices):
                next_ind = indices[i]
                spcs = next_ind-ind-1 #extra -1 is for the star we just placed
                s = s + (" "*spcs) + "*"
                ind = next_ind
                i = i + 1
        lines.append(s.ljust(len(arr)))
        amplitude_i = amplitude_i - 1
    #convert to ints
    return lines


def main(stdscr):
    # Clear screen
    stdscr.clear()

    # This raises ZeroDivisionError when i == 10.
    for i in range(1, 9):
        v = i-10
        stdscr.addstr(i, 0, '10 divided by {} is {}'.format(v, 10/v))

    stdscr.refresh()
    stdscr.getkey()

if __name__ == "__main__":
    wrapper(curses_main)
