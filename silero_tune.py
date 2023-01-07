import warnings

import torch


def get_speech_timestamps(audio: torch.Tensor,
                          model,
                          threshold: float = 0.5,
                          sampling_rate: int = 16000,
                          min_speech_duration_ms: int = 250,
                          min_silence_duration_ms: int = 100,
                          preferred_min_speech_duration_ms: int = 250,
                          preferred_speech_duration_ms: int = 6000,
                          window_size_samples: int = 1536,
                          speech_pad_ms: int = 30,
                          return_seconds: bool = False,
                          visualize_probs: bool = False,
                          visualize_lens: bool = False):
    """
    This method is used for splitting long audios into speech chunks using silero VAD

    Parameters
    ----------
    audio: torch.Tensor, one dimensional
        One dimensional float torch.Tensor, other types are casted to torch if possible

    model: preloaded .jit silero VAD model

    threshold: float (default - 0.5)
        Speech threshold. Silero VAD outputs speech probabilities for each audio chunk, probabilities ABOVE this value are considered as SPEECH.
        It is better to tune this parameter for each dataset separately, but "lazy" 0.5 is pretty good for most datasets.

    sampling_rate: int (default - 16000)
        Currently silero VAD models support 8000 and 16000 sample rates

    min_speech_duration_ms: int (default - 250 milliseconds)
        Final speech chunks shorter min_speech_duration_ms are thrown out

    min_silence_duration_ms: int (default - 100 milliseconds)
        In the end of each speech chunk wait for min_silence_duration_ms before separating it.

    preferred_min_speech_duration_ms: int (default - 250 milliseconds)
        A hint of speech duration that the postprocessing logic will make use of to merge segments.
        The value must not be less than min_speech_duration_ms.

    preferred_speech_duration_ms: int (default - 600000 milliseconds)
        A hint of speech duration that the postprocessing logic will make use of to merge segments.
        The value must be way larger than min_speech_duration_ms.

    window_size_samples: int (default - 1536 samples)
        Audio chunks of window_size_samples size are fed to the silero VAD model.
        WARNING! Silero VAD models were trained using 512, 1024, 1536 samples for 16000 sample rate and 256, 512, 768 samples for 8000 sample rate.
        Values other than these may affect model perfomance!!

    speech_pad_ms: int (default - 30 milliseconds)
        Final speech chunks are padded by speech_pad_ms each side

    return_seconds: bool (default - False)
        whether return timestamps in seconds (default - samples)

    visualize_probs: bool (default - False)
        whether draw prob hist or not

    visualize_lens: bool (default - False)
        whether draw histogram for speech chunks or not

    Returns
    ----------
    speeches: list of dicts
        list containing ends and beginnings of speech chunks (samples or seconds based on return_seconds)
    """

    if not torch.is_tensor(audio):
        try:
            audio = torch.Tensor(audio)
        except:
            raise TypeError("Audio cannot be casted to tensor. Cast it manually")

    if preferred_min_speech_duration_ms < min_speech_duration_ms:
        raise ValueError("preferred_min_speech_duration_ms must not be less than min_speech_duration_ms")

    if preferred_speech_duration_ms <= min_speech_duration_ms:
        raise ValueError("preferred_speech_duration_ms should be way larger than min_speech_duration_ms")

    if len(audio.shape) > 1:
        for i in range(len(audio.shape)):  # trying to squeeze empty dimensions
            audio = audio.squeeze(0)
        if len(audio.shape) > 1:
            raise ValueError("More than one dimension in audio. Are you trying to process audio with 2 channels?")

    if sampling_rate > 16000 and (sampling_rate % 16000 == 0):
        step = sampling_rate // 16000
        sampling_rate = 16000
        audio = audio[::step]
        warnings.warn('Sampling rate is a multiply of 16000, casting to 16000 manually!')
    else:
        step = 1

    if sampling_rate == 8000 and window_size_samples > 768:
        warnings.warn(
            'window_size_samples is too big for 8000 sampling_rate! Better set window_size_samples to 256, 512 or 768 '
            'for 8000 sample rate!')
    if window_size_samples not in [256, 512, 768, 1024, 1536]:
        warnings.warn(
            'Unusual window_size_samples! Supported window_size_samples:\n - [512, 1024, 1536] for 16000 '
            'sampling_rate\n - [256, 512, 768] for 8000 sampling_rate')

    model.reset_states()
    min_speech_samples = sampling_rate * min_speech_duration_ms / 1000
    min_silence_samples = sampling_rate * min_silence_duration_ms / 1000
    preferred_min_speech_samples = sampling_rate * preferred_min_speech_duration_ms / 1000
    preferred_speech_samples = sampling_rate * preferred_speech_duration_ms / 1000
    speech_pad_samples = sampling_rate * speech_pad_ms / 1000

    audio_length_samples = len(audio)

    speech_probs = []
    for current_start_sample in range(0, audio_length_samples, window_size_samples):
        chunk = audio[current_start_sample: current_start_sample + window_size_samples]
        if len(chunk) < window_size_samples:
            chunk = torch.nn.functional.pad(chunk, (0, int(window_size_samples - len(chunk))))
        speech_prob = model(chunk, sampling_rate).item()
        speech_probs.append(speech_prob)

    triggered = False
    speeches = []
    current_speech = {}
    neg_threshold = threshold - 0.15
    temp_end = 0
    # roughly 100ms in the case of sampling_rate=16000 and window_size_samples=1536
    n_look_back = 10
    n_look_forward = 10

    for i, speech_prob in enumerate(speech_probs):
        if (speech_prob >= threshold) and temp_end:
            temp_end = 0

        if (speech_prob >= threshold) and not triggered:
            triggered = True
            current_speech['start'] = window_size_samples * i
            continue

        # stop when the number of samples is larger than preferred.
        if (speech_prob >= threshold) and triggered \
                and window_size_samples * i - current_speech['start'] >= preferred_speech_samples:
            min_prob_ii = i
            for ii in range(max(i - n_look_back, 0), i, 1):
                if window_size_samples * ii <= current_speech['start']:
                    continue
                if speech_probs[ii] < speech_probs[min_prob_ii]:
                    min_prob_ii = ii
            current_speech['end'] = window_size_samples * min_prob_ii
            speeches.append(current_speech)

            if min_prob_ii != i:
                current_speech = {'start': window_size_samples * (min_prob_ii + 1)}
                continue
            else:
                temp_end = 0
                current_speech = {}
                triggered = False
                continue

        if (speech_prob < neg_threshold) and triggered:
            if not temp_end:
                temp_end = window_size_samples * i
            if (window_size_samples * i) - temp_end < min_silence_samples:
                continue
            elif (window_size_samples * i) - temp_end < preferred_min_speech_samples:
                for ii in range(i, min(i + n_look_forward, len(speech_probs)), 1):
                    if speech_probs[ii] >= threshold:
                        continue
            else:
                current_speech['end'] = temp_end
                if (current_speech['end'] - current_speech['start']) > min_speech_samples:
                    speeches.append(current_speech)
                temp_end = 0
                current_speech = {}
                triggered = False
                continue

    if current_speech:
        current_speech['end'] = audio_length_samples
        speeches.append(current_speech)

    for i, speech in enumerate(speeches):
        if i == 0:
            speech['start'] = int(max(0, speech['start'] - speech_pad_samples))
        if i != len(speeches) - 1:
            silence_duration = speeches[i + 1]['start'] - speech['end']
            if silence_duration < 2 * speech_pad_samples:
                speech['end'] += int(silence_duration // 2)
                speeches[i + 1]['start'] = int(max(0, speeches[i + 1]['start'] - silence_duration // 2))
            else:
                speech['end'] += int(speech_pad_samples)
        else:
            speech['end'] = int(min(audio_length_samples, speech['end'] + speech_pad_samples))

    # make sure visualization logic doesn't depend on `return_seconds`
    if visualize_lens:
        make_lens_visualization(speeches, sampling_rate)

    if return_seconds:
        for speech_dict in speeches:
            speech_dict['start'] = round(speech_dict['start'] / sampling_rate, 3)
            speech_dict['end'] = round(speech_dict['end'] / sampling_rate, 3)
    elif step > 1:
        for speech_dict in speeches:
            speech_dict['start'] *= step
            speech_dict['end'] *= step

    if visualize_probs:
        make_probs_visualization(speech_probs, window_size_samples / sampling_rate)

    return speeches


def make_probs_visualization(probs, step):
    import pandas as pd
    import matplotlib.pyplot as plt
    df = pd.DataFrame({'probs': probs},
                      index=[x * step for x in range(len(probs))])
    df.plot(figsize=(16, 8),
            kind='area', ylim=[0, 1.05],
            xlim=[0, len(probs) * step],
            xlabel='seconds',
            ylabel='speech probability',
            colormap='tab20')
    plt.show()


def make_lens_visualization(speeches, sampling_rate):
    import matplotlib.pyplot as plt

    speech_lens = []
    for speech in speeches:
        speech_lens.append((speech['end'] - speech['start']) / sampling_rate)

    plt.hist(speech_lens, bins=12)
    plt.show()