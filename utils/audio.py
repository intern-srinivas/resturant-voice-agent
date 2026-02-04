import base64
import audioop


class AudioConverter:
    """Utility class for audio format conversions."""

    @staticmethod
    def decode_mulaw(data: bytes) -> bytes:
        """Decode mulaw audio to linear PCM."""
        return audioop.ulaw2lin(data, 2)

    @staticmethod
    def encode_mulaw(data: bytes) -> bytes:
        """Encode linear PCM audio to mulaw."""
        return audioop.lin2ulaw(data, 2)

    @staticmethod
    def base64_decode(data: str) -> bytes:
        """Decode base64 encoded audio data."""
        return base64.b64decode(data)

    @staticmethod
    def base64_encode(data: bytes) -> str:
        """Encode audio data to base64."""
        return base64.b64encode(data).decode("utf-8")

    @staticmethod
    def resample(data: bytes, from_rate: int, to_rate: int, width: int = 2) -> bytes:
        """Resample audio data from one sample rate to another."""
        if from_rate == to_rate:
            return data
        return audioop.ratecv(data, width, 1, from_rate, to_rate, None)[0]
