"""STT platform for Doubao ASR HTTP."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterable

import aiohttp

from homeassistant.components import stt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_TIMEOUT,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Doubao ASR STT entity."""
    async_add_entities([DoubaoAsrSttEntity(entry)])


class DoubaoAsrSttEntity(stt.SpeechToTextEntity):
    """Doubao ASR STT entity."""

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
        """Process audio stream via Doubao ASR HTTP service."""
        cfg = self._merged
        host = cfg[CONF_HOST]
        port = cfg[CONF_PORT]
        timeout_sec = int(cfg.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))

        url = f"http://{host}:{port}/transcribe"

        try:
            audio_bytes = b"".join([chunk async for chunk in stream])

            timeout = aiohttp.ClientTimeout(total=timeout_sec)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                data = aiohttp.FormData()
                data.add_field("file", audio_bytes, filename="audio.wav",
                               content_type="audio/wav")
                async with session.post(url, data=data) as resp:
                    result = await resp.json()

            if result.get("success"):
                text = result.get("text", "").strip()
                return stt.SpeechResult(
                    text if text else None,
                    stt.SpeechResultState.SUCCESS if text else stt.SpeechResultState.ERROR,
                )
            else:
                _LOGGER.warning("Doubao ASR error: %s", result.get("error", "unknown"))
                return stt.SpeechResult(None, stt.SpeechResultState.ERROR)

        except Exception:
            _LOGGER.exception("Doubao ASR STT failed")
            return stt.SpeechResult(None, stt.SpeechResultState.ERROR)
