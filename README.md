# Repeat After Me

![](https://img.shields.io/badge/python-3.8+-blue.svg)

A python script that generates repeat-after-me audios for learning languages.

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
ram is nothing without it.

## FAQ

*Can I use other audio formats such as mp3?*

Audio decoding and encoding are handled by torchaudio, all supported format are listed 
[here](https://pytorch.org/audio/stable/backend.html#torchaudio.backend.sox_io_backend.load).
It's worth noting that .wav support is out of the box, and extra efforts are required
if you want to use other formats such as .mp3. Please refer to the torchaudio doc. Another way
to walk around this is to use ffmpeg, or any other tools you can find on the internet that
can handle conversions between different audio formats. Though it's outside the scope.