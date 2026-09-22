from enum import Enum


class TrackTypes(str, Enum):
    SHOT = "Shot"
    ASSET = "Asset"
    AUDIO = "Audio"
    CUSTOM = "Custom"

    @staticmethod
    def values():
        return (track_type for track_type in TrackTypes)


AssetTypes = Enum("AssetTypes", "MDL USD AUDIO PRIM")
