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
    """Wrapper for custom wavelink.Filter"""

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
    """Manages custom filters"""

    def __init__(self):
        self._modes = {
            "boost": self.boost,
            "destroy1": self.destroy1,
            "destroy2": self.destroy2,
            "destroy3": self.destroy3,
            "spin": self.spin,
            "nightcore": self.nightcore,
        }

    @property
    def modes(self) -> dict:
        return self._modes

    @property
    def clear(self) -> Filter:
        return Filter(equalizer=Equalizer.flat())

    @property
    def boost(self) -> CustomFilter:
        return CustomFilter("boost", "Boosts the bass.", equalizer=Equalizer.boost())

    @property
    def destroy1(self) -> CustomFilter:
        return CustomFilter(
            "destroy",
            "Destroy the audio. 1",
            distortion=Distortion(
                scale=0.5, sin_offset=0, sin_scale=0.5, cos_offset=0, cos_scale=0.5
            ),
        )

    @property
    def destroy2(self) -> CustomFilter:
        return CustomFilter(
            "destroy",
            "Destroy the audio. 2",
            distortion=Distortion(
                scale=1.5, sin_offset=0.5, sin_scale=1.5, cos_offset=0.5, cos_scale=1.5
            ),
        )

    @property
    def destroy3(self) -> CustomFilter:
        return CustomFilter(
            "destroy",
            "Destroy the audio. 3",
            distortion=Distortion(
                scale=1, sin_offset=1, sin_scale=1, cos_offset=1, cos_scale=1
            ),
        )

    @property
    def spin(self) -> CustomFilter:
        return CustomFilter("spin", "Guess what this does.", rotation=Rotation(0.5))

    @property
    def nightcore(self) -> CustomFilter:
        return CustomFilter(
            "nightcore",
            "For people with mental issues.",
            timescale=Timescale(pitch=1.25, speed=1.15, rate=1.15),
        )
