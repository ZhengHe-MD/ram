class SegmentSetting:
    def __init__(self, name: str,
                 speed: float = 1.0,
                 pause: float = 1.0,
                 preferred_speech_duration_ms: int = 6000):
        self.name = name
        self.speed = speed
        self.pause = pause
        self.preferred_speech_duration_ms = preferred_speech_duration_ms

    @property
    def min_silence_duration(self):
        if self.name == 'easy':
            return 25
        elif self.name == 'medium':
            return 50
        else:
            return 100


class InvalidSegmentSettingNameException(Exception):
    """Raised when the input name is unsupported"""
    pass


def new_segment_setting(name: str):
    if name == 'easy':
        return SegmentSetting(name, speed=0.85, pause=2, preferred_speech_duration_ms=3000)
    elif name == 'medium':
        return SegmentSetting(name, speed=0.95, pause=1.5, preferred_speech_duration_ms=6000)
    elif name == 'hard':
        return SegmentSetting(name, speed=1.0, pause=1.0, preferred_speech_duration_ms=8000)
    else:
        raise InvalidSegmentSettingNameException
