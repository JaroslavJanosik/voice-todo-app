#!/bin/sh
set -eu

if [ "${WHISPER_PRELOAD_MODEL:-0}" = "1" ]; then
  python preload_transcription_runtime.py
fi

exec "$@"
