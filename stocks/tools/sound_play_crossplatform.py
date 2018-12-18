# -*- coding: utf-8 -*-
'''
Cross-platform Sound Playing with Standard Libs only, No Sound file is required, No install is required, Python2 / Python3.
windowsound is MS Windows-only, pygame need third party modules, this one depends on nothing.
Valid values on the Tuple Argument are positive Integers >0 and <128.
Theres no point to use something like random.randint() because you dont feel the difference.
'''

import os, sys
from tempfile import gettempdir
from subprocess import call


def beep(soundFileName=os.path.join(gettempdir(), "beep.wav")):
    """Cross-platform Sound Playing with StdLib only,No Sound file required."""
    wavefile = soundFileName
    if not os.path.isfile(wavefile) or not os.access(wavefile, os.R_OK):
        waveform = (79, 45, 32, 50, 99, 113, 126, 127)
        with open(wavefile, "w+") as wave_file:
            for sample in range(0, 1000, 1):
                for wav in range(0, 8, 1):
                    wave_file.write(chr(waveform[wav]))
    if sys.platform.startswith("linux"):
        return call("chrt -i 0 aplay '{fyle}'".format(fyle=wavefile), shell=1)
    if sys.platform.startswith("darwin"):
        return call("afplay '{fyle}'".format(fyle=wavefile), shell=True)
    if sys.platform.startswith("win"):  # FIXME: This is Ugly.
        return call("start /low /min '{fyle}'".format(fyle=wavefile), shell=1)


if __name__ in '__main__':
    beep()
