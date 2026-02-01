from .nodes import (
    TranscribeSrt,
)

NODE_CLASS_MAPPINGS = {
    "TranscribeSrt": TranscribeSrt,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TranscribeSrt": "Transcribe To Srt",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
