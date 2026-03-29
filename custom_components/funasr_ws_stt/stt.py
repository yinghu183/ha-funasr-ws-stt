"""STT platform for FunASR WebSocket."""

from __future__ import annotations

import asyncio
import io
import json
import logging
import wave
from collections.abc import AsyncIterable

import websockets

from homeassistant.components import stt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONF_HOST,
    CONF_HOTWORDS,
    CONF_ITN,
    CONF_MODE,
    CONF_NAME,
    CONF_PORT,
    CONF_SSL,
    CONF_TIMEOUT,
    DEFAULT_HOTWORDS,
    DEFAULT_ITN,
    DEFAULT_MODE,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

CHUNK_SIZE = 3200  # 100ms at 16k mono 16bit


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up FunASR WS STT entity."""
    async_add_entities([FunAsrWsSttEntity(entry)])


class FunAsrWsSttEntity(stt.SpeechToTextEntity):
    """FunASR WebSocket STT entity."""

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}-stt"
        self._attr_name = entry.data[CONF_NAME]

    @property
    def _merged(self) -> dict:
        return {**self._entry.data, **self._entry.options}

    @property
    def supported_languages(self) -> list[str]:
        return ["zh-CN", "en-US"]

    @property
    def supported_formats(self) -> list[stt.AudioFormats]:
        return [stt.AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[stt.AudioCodecs]:
        return [stt.AudioCodecs.PCM]

    @property
    def supported_bit_rates(self) -> list[stt.AudioBitRates]:
        return [stt.AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[stt.AudioSampleRates]:
        return [stt.AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[stt.AudioChannels]:
        return [stt.AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(
        self, metadata: stt.SpeechMetadata, stream: AsyncIterable[bytes]
    ) -> stt.SpeechResult:
        """Process stream with FunASR websocket server."""
        cfg = self._merged
        host = cfg[CONF_HOST]
        port = cfg[CONF_PORT]
        use_ssl = cfg[CONF_SSL]
        mode = cfg.get(CONF_MODE, DEFAULT_MODE)
        hotwords = cfg.get(CONF_HOTWORDS, DEFAULT_HOTWORDS)
        itn = bool(cfg.get(CONF_ITN, DEFAULT_ITN))
        timeout = int(cfg.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))

        try:
            wav_bytes = b"".join([chunk async for chunk in stream])
            pcm, sample_rate = _wav_to_pcm(wav_bytes)

            uri = f"wss://{host}:{port}" if use_ssl else f"ws://{host}:{port}"
            ssl_ctx = None
            if use_ssl:
                import ssl

                ssl_ctx = ssl.SSLContext()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl.CERT_NONE

            async with asyncio.timeout(timeout):
                transcript = await _transcribe_via_funasr_ws(
                    uri=uri,
                    ssl_context=ssl_ctx,
                    pcm=pcm,
                    sample_rate=sample_rate,
                    mode=mode,
                    hotwords=hotwords,
                    itn=itn,
                )

            if transcript is None:
                return stt.SpeechResult(None, stt.SpeechResultState.ERROR)

            return stt.SpeechResult(transcript, stt.SpeechResultState.SUCCESS)
        except Exception:  # noqa: BLE001
            _LOGGER.exception("FunASR websocket STT failed")
            return stt.SpeechResult(None, stt.SpeechResultState.ERROR)


def _wav_to_pcm(wav_bytes: bytes) -> tuple[bytes, int]:
    """Extract PCM frames and sample rate from WAV bytes."""
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        sample_rate = wf.getframerate()
        if channels != 1:
            raise ValueError(f"unsupported_channels:{channels}")
        if sampwidth != 2:
            raise ValueError(f"unsupported_sample_width:{sampwidth}")
        pcm = wf.readframes(wf.getnframes())
    return pcm, sample_rate


async def _transcribe_via_funasr_ws(
    *,
    uri: str,
    ssl_context,
    pcm: bytes,
    sample_rate: int,
    mode: str,
    hotwords: str,
    itn: bool,
) -> str | None:
    """Send PCM stream to FunASR websocket and collect final transcript."""
    init_payload = {
        "mode": mode,
        "chunk_size": [5, 10, 5],
        "chunk_interval": 10,
        "encoder_chunk_look_back": 4,
        "decoder_chunk_look_back": 0,
        "audio_fs": sample_rate,
        "wav_name": "ha",
        "wav_format": "pcm",
        "is_speaking": True,
        "hotwords": hotwords or "",
        "itn": bool(itn),
    }

    final_text = ""

    async with websockets.connect(
        uri,
        subprotocols=["binary"],
        ping_interval=None,
        ssl=ssl_context,
        max_size=8 * 1024 * 1024,
    ) as ws:
        await ws.send(json.dumps(init_payload, ensure_ascii=False))

        for i in range(0, len(pcm), CHUNK_SIZE):
            await ws.send(pcm[i : i + CHUNK_SIZE])

        await ws.send(json.dumps({"is_speaking": False}))

        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            text = (data.get("text") or "").strip()
            if text:
                final_text = text

            if data.get("is_final") or data.get("mode") == "offline":
                break

    return final_text.strip() or None
