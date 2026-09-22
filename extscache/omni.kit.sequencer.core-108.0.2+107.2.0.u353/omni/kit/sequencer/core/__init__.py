from enum import Enum

import omni.ext
import omni.kit.commands
import omni.usd

from .scripts import sequencer_settings
from .scripts.sequencer_audio_commands import SequencerUIStreamAudioCommand
from .scripts.sequencer_commands import (
    SequencerClipCreateCommand,
    SequencerClipDuplicateCommand,
    SequencerClipSetAnimationCommand,
    SequencerClipSetTargetCommand,
    SequencerClipUpdateTimeCommand,
    SequencerCreateReferenceCommand,
    SequencerCreateSequenceCommand,
    SequencerSetTargetCommand,
    SequencerSettingsSetSnapToFrameCommand,
    SequencerTrackCreateCommand,
    SequencerTrackMoveCommand,
    SequencerTrackVisibleSetCommand,
    SequencerClipUpdateTrimCommand,
    SequencerClipSplitCommand,
    SequencerSetChildLocation,
)
from .scripts.sequencer_track_types import AssetTypes, TrackTypes


class SequencerExt(omni.ext.IExt):
    def on_startup(self):
        omni.kit.commands.register(SequencerCreateSequenceCommand)
        omni.kit.commands.register(SequencerCreateReferenceCommand)
        # ---------------- Track commands
        omni.kit.commands.register(SequencerTrackCreateCommand)
        omni.kit.commands.register(SequencerTrackMoveCommand)
        omni.kit.commands.register(SequencerSetChildLocation)
        omni.kit.commands.register(SequencerTrackVisibleSetCommand)
        omni.kit.commands.register(SequencerSetTargetCommand)

        # ---------------- Clip commands
        omni.kit.commands.register(SequencerClipCreateCommand)
        omni.kit.commands.register(SequencerClipDuplicateCommand)
        omni.kit.commands.register(SequencerClipSetTargetCommand)
        omni.kit.commands.register(SequencerClipSetAnimationCommand)
        omni.kit.commands.register(SequencerClipUpdateTimeCommand)
        omni.kit.commands.register(SequencerClipUpdateTrimCommand)
        omni.kit.commands.register(SequencerClipSplitCommand)

        # ---------------- Sequencer Settings
        omni.kit.commands.register(SequencerSettingsSetSnapToFrameCommand)
        omni.kit.commands.register(SequencerSettingsSetSnapToFrameCommand)
        omni.kit.commands.register(SequencerUIStreamAudioCommand)

    def on_shutdown(self):
        omni.kit.commands.unregister(SequencerCreateSequenceCommand)
        omni.kit.commands.unregister(SequencerCreateReferenceCommand)
        # ---------------- Track commands
        omni.kit.commands.unregister(SequencerTrackCreateCommand)
        omni.kit.commands.unregister(SequencerTrackMoveCommand)
        omni.kit.commands.unregister(SequencerSetChildLocation)
        omni.kit.commands.unregister(SequencerTrackVisibleSetCommand)
        omni.kit.commands.unregister(SequencerSetTargetCommand)

        # ---------------- Clip commands
        omni.kit.commands.unregister(SequencerClipCreateCommand)
        omni.kit.commands.unregister(SequencerClipDuplicateCommand)
        omni.kit.commands.unregister(SequencerClipSetTargetCommand)
        omni.kit.commands.unregister(SequencerClipSetAnimationCommand)
        omni.kit.commands.unregister(SequencerClipUpdateTimeCommand)
        omni.kit.commands.unregister(SequencerClipUpdateTrimCommand)
        omni.kit.commands.unregister(SequencerClipSplitCommand)

        # ---------------- Sequencer Settings
        omni.kit.commands.unregister(SequencerSettingsSetSnapToFrameCommand)
        omni.kit.commands.unregister(SequencerSettingsSetSnapToFrameCommand)
        omni.kit.commands.unregister(SequencerUIStreamAudioCommand)
