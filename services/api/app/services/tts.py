from pathlib import Path
import asyncio
import wave
import math
import struct
from app.core.config import get_settings


class SpeechService:
    async def synthesize(self, text: str, language: str, output_path: Path) -> Path:
        settings = get_settings()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if settings.tts_provider == "google":
            try:
                return await self._google_tts(text, language, output_path)
            except Exception as exc:
                # Keep narration resilient: if cloud TTS fails, fall back below.
                # Log the reason so the placeholder tone is not silent.
                print(f"[tts] Google TTS failed, using placeholder tone: {exc!r}", flush=True)
        else:
            # Demo provider: use free online gTTS so the narration is real speech
            # (no cloud credentials required). Falls back to a beep if it fails
            # (e.g. no internet access).
            try:
                return await self._gtts(text, language, output_path)
            except Exception:
                pass
        self._write_placeholder_wav(output_path, seconds=max(5, min(18, len(text) // 18)))
        return output_path

    async def _gtts(self, text: str, language: str, output_path: Path) -> Path:
        from gtts import gTTS

        lang = self._gtts_lang(language)

        def _run() -> None:
            # gTTS produces MP3; ffmpeg (renderer) sniffs the format by content,
            # so writing MP3 bytes to the given path works regardless of extension.
            gTTS(text=text, lang=lang).save(str(output_path))

        # gTTS makes a blocking network call; run it off the event loop.
        await asyncio.get_running_loop().run_in_executor(None, _run)
        return output_path

    @staticmethod
    def _gtts_lang(language: str) -> str:
        # Map narration language codes like "ja-JP" / "en-US" to gTTS codes "ja" / "en".
        if not language:
            return "en"
        return language.split("-")[0].lower() or "en"

    async def _google_tts(self, text: str, language: str, output_path: Path) -> Path:
        from google.api_core.client_options import ClientOptions
        from google.cloud import texttospeech

        # Text-to-Speech requires an explicit billing/quota project when the
        # credentials don't carry one (e.g. Workload Identity Federation in CI),
        # otherwise the call 403s and narration falls back to a placeholder tone.
        project = get_settings().gcp_project_id
        options = ClientOptions(quota_project_id=project) if project else None
        client = texttospeech.TextToSpeechClient(client_options=options)
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        output_path.write_bytes(response.audio_content)
        return output_path

    def _write_placeholder_wav(self, output_path: Path, seconds: int = 10) -> None:
        sample_rate = 44100
        frequency = 440.0
        amplitude = 0.12
        n_samples = seconds * sample_rate
        with wave.open(str(output_path), "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            for i in range(n_samples):
                value = int(32767 * amplitude * math.sin(2 * math.pi * frequency * i / sample_rate))
                wav.writeframes(struct.pack("<h", value))
