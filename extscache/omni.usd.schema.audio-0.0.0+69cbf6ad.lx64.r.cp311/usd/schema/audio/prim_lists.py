import OmniAudioSchema

def get_audio_prim_list():
    return [
        ("Spatial Sound", "OmniSound", {}),
        (
            "Non-Spatial Sound",
            "OmniSound",
            {OmniAudioSchema.Tokens.auralMode: OmniAudioSchema.Tokens.nonSpatial}
        ),
        ("Listener", "OmniListener", {})
    ]

