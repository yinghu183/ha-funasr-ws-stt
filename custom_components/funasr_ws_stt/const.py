"""Constants for FunASR WebSocket STT integration."""

DOMAIN = "funasr_ws_stt"

CONF_NAME = "name"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SSL = "ssl"
CONF_MODE = "mode"
CONF_HOTWORDS = "hotwords"
CONF_ITN = "itn"
CONF_TIMEOUT = "timeout"

DEFAULT_NAME = "FunASR WebSocket STT"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 10095
DEFAULT_SSL = False
DEFAULT_MODE = "offline"
DEFAULT_HOTWORDS = ""
DEFAULT_ITN = True
DEFAULT_TIMEOUT = 30

MODES = ["offline", "2pass", "online"]
