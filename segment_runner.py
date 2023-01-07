import logging

import torch
import torchaudio.backend.no_backend

from segment_setting import SegmentSetting, new_segment_setting
from silero_tune import get_speech_timestamps


class SegmentRunner:
    def __init__(self):
        self.model, utils = torch.hub.load(repo_or_dir="snakers4/silero-vad", model="silero_vad")
        (_, self.save_audio, self.read_audio, _, _) = utils
        self.get_speech_timestamps = get_speech_timestamps

    def run(self, input_audio: str, output_audio: str, level: str, verbose: bool = False):
        setting = new_segment_setting(level)
        # load audio
        if verbose:
            logging.info(f'load audio from {input_audio}.')
        audio, sr = torchaudio.load(input_audio)

        # merge channels
        if audio.size(0) > 1:
            audio = audio.mean(dim=0, keepdim=True)

        # preprocess
        if verbose:
            logging.info(f'adjust the speed and sampling rate.')
        audio, sr = torchaudio.sox_effects.apply_effects_tensor(
            audio, sr, effects=[['speed', f'{setting.speed}'], ['rate', '16000']])
        audio = audio.squeeze(0)

        # segment
        if verbose:
            logging.info(f'generate the repeat-after-me audio.')
        timestamps = self.get_speech_timestamps(audio=audio,
                                                model=self.model,
                                                preferred_speech_duration_ms=setting.preferred_speech_duration_ms,
                                                min_silence_duration_ms=setting.min_silence_duration)
        segments = SegmentRunner.smooth([[ts['start'], ts['end']] for ts in timestamps])
        # interpolate
        interpolated = []
        for segment in segments:
            start, end = segment[0], segment[1]
            interpolated.append(audio[start:end])
            interpolated.append(torch.zeros(int((end - start) * setting.pause / setting.speed)))
        logging.info(f'save generated audio to {output_audio}.')
        self.save_audio(output_audio, torch.cat(interpolated), sampling_rate=16000)

    @staticmethod
    def smooth(segments):
        """leave spaces at the start and end of each segment so that it sounds more natural"""
        smoothed_segments = []
        for i, segment in enumerate(segments):
            start, end = segment
            if i > 0:
                start = max(
                    segments[i - 1][1] + 0.001,
                    segments[i - 1][1] + (start - segments[i - 1][1]) / 2 + 0.001,
                    start - 1)
            else:
                start = max(0, start - 1)

            if i < len(segments) - 1:
                end = min(
                    end + 1,
                    segments[i + 1][0] - (segments[i + 1][0] - end) / 2 - 0.001,
                    segments[i + 1][0] - 0.001
                )
            smoothed_segments.append([round(start, 3), round(end, 3)])
        return smoothed_segments
