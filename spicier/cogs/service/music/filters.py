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
            "piano": Filter(equalizer=Equalizer.piano()),
        }

    @property
    def modes(self) -> dict:
        return self._modes

    @property
    def clear(self) -> Filter:
        return Filter(
            equalizer=Equalizer(),
            karaoke=Karaoke(),
            timescale=Timescale(),
            tremolo=Tremolo(),
            vibrato=Vibrato(),
            rotation=Rotation(),
            distortion=Distortion(),
            lowpass=LowPass(),
            channelmix=ChannelMix(),
        )
