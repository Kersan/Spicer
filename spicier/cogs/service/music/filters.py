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
            "destroy1": CustomFilter(
                "destroy",
                "Destroy the audio. 1",
                distortion=Distortion(
                    scale=0.5, sin_offset=0, sin_scale=0.5, cos_offset=0, cos_scale=0.5
                ),
            ),
            "destroy2": CustomFilter(
                "destroy",
                "Destroy the audio. 2",
                distortion=Distortion(
                    scale=1.5,
                    sin_offset=0.5,
                    sin_scale=1.5,
                    cos_offset=0.5,
                    cos_scale=1.5,
                ),
            ),
            "destroy3": CustomFilter(
                "destroy",
                "Destroy the audio. 3",
                distortion=Distortion(
                    scale=1,
                    sin_offset=1,
                    sin_scale=1,
                    cos_offset=1,
                    cos_scale=1,
                ),
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
