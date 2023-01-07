# Repeat After Me

![](https://img.shields.io/badge/python-3.8+-blue.svg)

A python script that generates repeat-after-me audios for learning languages.

## Installation

Just clone this repo:

```shell
$ git clone https://github.com/ZhengHe-MD/ram.git
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

checkout full options with the following command:

```shell
$ python ram -h
```
