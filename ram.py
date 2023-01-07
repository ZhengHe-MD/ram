import argparse
import logging

from segment_runner import SegmentRunner


def execute():
    parser = argparse.ArgumentParser(prog="python ram",
                                     description="generate repeat-after-me audios for language learning",
                                     epilog="github.com/ZhengHe-MD/ram")

    parser.add_argument('audio')
    parser.add_argument('-o', '--output-audio', default='out.wav')
    parser.add_argument('-l', '--level', choices=['easy', 'medium', 'hard'], default='easy')
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()
    runner = SegmentRunner()
    try:
        runner.run(args.audio, args.output_audio, args.level, verbose=args.verbose)
    except RuntimeError as e:
        logging.error(e)
