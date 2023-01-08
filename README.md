# RAM

![](https://img.shields.io/badge/python-3.8+-blue.svg)

RAM stands for Repeat-After-Me. It's a python script that can interpolate your audios with blanks that
let you do repeat-after practice for language learning purposes. You can specify the difficulty level
of the generated audio. The easier the level, the shorter the segments, the longer the blanks and the
lower the playing speed. And it supports a high range of languages thanks to the [silero-vad](https://github.com/snakers4/silero-vad) project.

## Demo

Use the audio from Professor Brian Harvey talking about cheating in class as an example:

* [original](https://raw.githubusercontent.com/ZhengHe-MD/blog/master/source/_posts/repeat-after-me/dont-cheat.mp3)
* [easy](https://raw.githubusercontent.com/ZhengHe-MD/blog/master/source/_posts/repeat-after-me/dont-cheat-easy.mp3)
* [medium](https://raw.githubusercontent.com/ZhengHe-MD/blog/master/source/_posts/repeat-after-me/dont-cheat-medium.mp3)
* [hard](https://raw.githubusercontent.com/ZhengHe-MD/blog/master/source/_posts/repeat-after-me/dont-cheat-hard.mp3)

## Installation

Clone this repo:

```shell
$ git clone https://github.com/ZhengHe-MD/ram.git
```

Install Python dependencies:

```shell
# step out of ram directory to go through usages.
$ cd ram && pip install -r requirements.txt && cd ..
```

## Usage

Suppose the current directory contains this repo, basic usages are:

```shell
# generates out.wav in current directory with difficulty level of easy
$ python ram path/to/audio.wav 

# specify the difficulty level
$ python ram path/to/audio.wav --level=hard

# specify the output audio file
$ python ram path/to/audio.wav --level=medium --output-audio ./audio-medium.wav
```

Checkout full options with the following command:

```shell
$ python ram -h
```

## Acknowledgement

Special thanks should be given to the project [snakers4/silero-vad](https://github.com/snakers4/silero-vad).
RAM is nothing without it.

## FAQ

*Can I use other audio formats such as mp3?*

Audio decoding and encoding are handled by torchaudio, all supported format are listed 
[here](https://pytorch.org/audio/stable/backend.html#torchaudio.backend.sox_io_backend.load).
It's worth noting that .wav support is out of the box, and extra efforts are required
if you want to use other formats such as .mp3. Please refer to the torchaudio doc. Another way
to walk around this is to use ffmpeg, or any other tools you can find on the internet that
can handle conversions between different audio formats. Though it's outside the scope.
