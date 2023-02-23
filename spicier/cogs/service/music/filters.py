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


class CustomFilter(Filter):
    def __init__(self, name: str, descritpion: str, **kwargs):
        super().__init__(**kwargs)

        self._name = name
        self._description = descritpion

    @property
    def description(self) -> str:
        return self._description
    
    @property
    def name(self) -> str:
        return self._name


class CustomFilters:
    def __init__(self):
        self._modes = {
            "boost": CustomFilter(
                "boost", "Boosts the bass.", equalizer=Equalizer.boost()
            ),
            "destroy": CustomFilter(
                "destroy", "Destroy the audio.", distortion=Distortion(scale=2)
            ),
            "spin": CustomFilter(
                "spin", "Guess what this does.", rotation=Rotation(0.5)
            ),
            "nightcore": CustomFilter(
                "nightcore",
                "For people with mental issues.",
                timescale=Timescale(pitch=1.25, speed=1.15, rate=1.15),
            ),
        }

    @property
    def modes(self) -> dict:
        return self._modes

    @property
    def clear(self) -> Filter:
        return Filter(equalizer=Equalizer.flat())
