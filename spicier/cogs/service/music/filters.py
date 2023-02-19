from typing import TypedDict

from wavelink import Filter
from wavelink.filters import (
    ChannelMix,
    Distortion,
    Equalizer,
    Karaoke,
    LowPass,
    Rotation,
    Timescale,
    Tremolo,
    Vibrato,
)


class CustomFilters:
    def __init__(self):
        self._modes = {
            "boost": Filter(equalizer=Equalizer.boost()),
            "flat": Filter(equalizer=Equalizer.flat()),
            "metal": Filter(equalizer=Equalizer.metal()),
            "spin": Filter(rotation=Rotation(0.6)),
        }

    @property
    def modes(self) -> dict:
        return self._modes

    @property
    def clear(self) -> Filter:
        return Filter(equalizer=Equalizer.flat())
