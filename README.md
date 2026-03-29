# FunASR WebSocket STT (Home Assistant custom integration)

Connect Home Assistant STT directly to a FunASR WebSocket server (`ws://host:port`) without adding an extra bridge process on the ASR host.

## Features

- Native Home Assistant **STT entity**
- Config flow (UI setup)
- Direct WebSocket call to FunASR (`offline` / `2pass` / `online`)
- HACS custom repository compatible
- Reliable input handling for both full WAV containers and raw PCM streams from Home Assistant

## Requirements

- Home Assistant 2025.1+
- FunASR websocket server reachable from HA machine
- Expected audio format from HA STT pipeline: WAV / PCM / 16k / mono / 16-bit

## Install via HACS custom repository

1. HACS → Integrations → ⋮ → **Custom repositories**
2. Add this repo URL as **Integration**:
   `https://github.com/yinghu183/ha-funasr-ws-stt`
3. Install `FunASR WebSocket STT`
4. Restart Home Assistant
5. Settings → Devices & Services → Add Integration → `FunASR WebSocket STT`

## Configuration

- **Host**: FunASR WS server host (for your setup: ASR host IP)
- **Port**: default `10095`
- **SSL**: false for local network plain WS
- **Mode**: `offline` recommended for final transcript
- **Hotwords**: optional
- **ITN**: true by default
- **Timeout**: request timeout in seconds

## Notes

- This integration avoids launching another persistent bridge service on your ASR host.
- It only adds execution on Home Assistant side when STT is invoked.
- Version `0.1.1` adds a WAV → raw PCM fallback path so HA streams without a RIFF header can still be sent to FunASR reliably.
