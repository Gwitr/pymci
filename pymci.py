"""
MIT License

Copyright (c) 2020 Wiktor Duniec

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import time
import random
import ctypes
import asyncio
from ctypes import wintypes

encoding = "CP%d" % (ctypes.windll.kernel32.GetACP())

def mm_errcheck(result, func, args):
    if result != 0:
        buf = (ctypes.c_char * 1024)()
        mm.mciGetErrorStringA(result, buf, 1024)
        raise Exception(buf.value.decode(encoding))

mm = ctypes.windll.winmm
mm.mciSendStringA.argtypes = (wintypes.LPCSTR, wintypes.LPSTR, wintypes.UINT, wintypes.HANDLE)
mm.mciSendStringA.errcheck = mm_errcheck

def mci_exec(text):
    text = text.encode(encoding)

    res = (ctypes.c_char * 1024)()
    mm.mciSendStringA(text, res, 1024, wintypes.HANDLE(0))

    return res.value.decode(encoding)

class SoundError(Exception):
    pass

LEFT  = 0
RIGHT = 1
BOTH  = 2

class Sound():

    sounds = []

    def __init__(self, path):
        """Creates a Sound object from a .WAV file at `path`."""
        
        self.path = path
        self.open = True
        self.playing = False
        
        maxid = 0
        for snd in Sound.sounds:
            if snd.open:
                if snd.sid > maxid:
                    maxid = snd.sid
        
        self.sid = maxid + 1
        self.mci_id = "MCISND.%08x" % self.sid

        if " " in path:
            raise SoundError("Path contains a space")
        mci_exec("open %s alias %s" % (path, self.mci_id))
        mci_exec("set %s time format milliseconds" % (self.mci_id))

        Sound.sounds.append(self)

    async def waitUntilStopped(self):
        """Coroutine: Waits until the song stopped playing."""
        while self.isPlaying():
            await asyncio.sleep(.025)

    def length(self):
        """Returns the length, in seconds."""
        return int(mci_exec("status %s length" % (self.mci_id))) / 1000

    def isPlaying(self):
        if self.position() == self.length():
            self.playing = False
        
        return self.playing

    def position(self, t=None):
        """
Without an argument: Returns the position, in seconds.
With an argument: Sets the position (specified in seconds)."""

        if not self.open:
            raise SoundError("Closed")

        if t is None:
            return int(mci_exec("status %s position" % self.mci_id)) / 1000
        else:
            f = self.playing
            if f:
                self.stop()
            mci_exec("seek %s to %d" % (self.mci_id, int(t * 1000)))
            if f:
                self.play()

    def volume(self, v=None, *, speaker=BOTH):
        """
Without an argument: Returns the volume of `speaker`.
With an argument: Sets the volume of `speaker`."""

        raise SoundError("Not implemented, since waveaudio devices don't support changing the volume.\nTODO: Use some wave module magic + temporary files to make it work")
        
        if v is not None:
            if speaker == BOTH:
                mci_exec("setaudio %s left volume to %d"  % (self.mci_id, v))
                mci_exec("setaudio %s right volume to %d" % (self.mci_id, v))
            elif speaker == LEFT:
                mci_exec("setaudio %s left volume to %d"  % (self.mci_id, v))
            elif speaker == RIGHT:
                mci_exec("setaudio %s right volume to %d" % (self.mci_id, v))
            else:
                raise SoundError("Invalid speaker")

        else:
            ...

    def play(self):
        """Plays the sound."""
        if not self.open:
            raise SoundError("Closed")
        mci_exec("play %s" % self.mci_id)
        self.playing = True

    def stop(self):
        """Stops the sound. Can only be resumed with `play()`."""
        if not self.open:
            raise SoundError("Closed")
        mci_exec("stop %s" % self.mci_id)
        self.playing = False

    def close(self):
        """Closes the sound."""
        if not self.open:
            raise SoundError("Closed")
        mci_exec("close %s" % self.mci_id)
        self.current_time = None
        self.open = False
        self.playing = False

    def pause(self):
        """Pauses the sound. Can be resumed with `play()` and `resume()`."""
        if not self.open:
            raise SoundError("Closed")
        mci_exec("pause %s" % self.mci_id)
        self.playing = False

    def resume(self):
        """Resumes the sound."""
        if not self.open:
            raise SoundError("Closed")
        mci_exec("resume %s" % self.mci_id)
        self.playing = True
