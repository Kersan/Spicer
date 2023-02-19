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
            "destroy": Filter(distortion=Distortion(scale=2)),
            "flat": Filter(equalizer=Equalizer.flat()),
            "spin": Filter(rotation=Rotation(0.5)),
            "nightcore": Filter(timescale=Timescale(pitch=1.25, speed=1.15, rate=1.15)),
        }

    @property
    def modes(self) -> dict:
        return self._modes

    @property
    def clear(self) -> Filter:
        return Filter(equalizer=Equalizer.flat())
