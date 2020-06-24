# pymci
Python "bindings" for the Win32 MCI API

The module contains 1 class, `Sound`.
It has the following methods:
* __init__(path) - Creates a new Sound object from the .WAV file at `path`.
* play() - Plays the sound.
* stop() - Stops the sound. It can be resumed with `play()`.
* pause() - Pauses the sound.
* resume() - Resumes the sound.
* volume(speaker=BOTH) - **NOT WORKING YET** Returns the current volume of the `speaker` speaker. The `speaker` argument can be LEFT, RIGHT or BOTH.
* volume(x, speaker=BOTH) - **NOT WORKING YET** Changes the volume for the `speaker` speaker.
* position() - Returns the position, in seconds.
* position(x) - Sets the position to `x`. (`x` is in seconds)
* length() - Returns the length of the sound, in seconds.
* waitUntilStopped() - A coroutine. Waits until the sound stops playing, and then returns.
* isPlaying() - Returns `True` if the sound is currently playing.
* close() - Stops and closes the sound. The sound can't be played after it is closed.
