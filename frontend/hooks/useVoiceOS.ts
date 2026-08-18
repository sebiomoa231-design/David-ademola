"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, toAudioUrl } from "@/lib/api";

export type VoiceOSState =
  | "idle"
  | "listening"
  | "thinking"
  | "generating_audio"
  | "speaking"
  | "success"
  | "error";

export type VoiceOSResult = {
  transcript: string;
  response: string;
  agentsUsed: string[];
  providersUsed: string[];
  planId?: string | null;
  taskDetails: Array<Record<string, unknown>>;
};

type VoiceOSOptions = {
  onResult?: (result: VoiceOSResult) => void;
  onError?: (message: string) => void;
};

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const value = String(reader.result || "");
      resolve(value.includes(",") ? value.slice(value.indexOf(",") + 1) : value);
    };
    reader.onerror = () => reject(reader.error || new Error("Could not read microphone audio"));
    reader.readAsDataURL(blob);
  });
}

function chooseMimeType(): string {
  if (typeof MediaRecorder === "undefined") return "audio/webm";
  const candidates = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg;codecs=opus"];
  return candidates.find((candidate) => MediaRecorder.isTypeSupported(candidate)) || "audio/webm";
}

export function useVoiceOS(options: VoiceOSOptions = {}) {
  const [state, setState] = useState<VoiceOSState>("idle");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [activeAction, setActiveAction] = useState("");
  const [volume, setVolume] = useState(0);
  const [error, setError] = useState("");
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const lastSpokenTextRef = useRef("");
  const [isPaused, setIsPaused] = useState(false);
  const inputAnalyserRef = useRef<AnalyserNode | null>(null);
  const inputAnimationRef = useRef<number | null>(null);
  const outputContextRef = useRef<AudioContext | null>(null);
  const outputSourceRef = useRef<MediaElementAudioSourceNode | null>(null);
  const outputAnalyserRef = useRef<AnalyserNode | null>(null);
  const outputAnimationRef = useRef<number | null>(null);

  const stopInputMeter = useCallback(() => {
    if (inputAnimationRef.current !== null) cancelAnimationFrame(inputAnimationRef.current);
    inputAnimationRef.current = null;
    inputAnalyserRef.current?.disconnect();
    inputAnalyserRef.current = null;
    setVolume(0);
  }, []);

  const stopOutputMeter = useCallback(() => {
    if (outputAnimationRef.current !== null) cancelAnimationFrame(outputAnimationRef.current);
    outputAnimationRef.current = null;
    outputSourceRef.current?.disconnect();
    outputSourceRef.current = null;
    outputAnalyserRef.current?.disconnect();
    outputAnalyserRef.current = null;
    const context = outputContextRef.current;
    outputContextRef.current = null;
    if (context && context.state !== "closed") void context.close();
    setVolume(0);
  }, []);

  const stopStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    stopInputMeter();
  }, [stopInputMeter]);

  const startInputMeter = useCallback((stream: MediaStream) => {
    try {
      const context = new AudioContext();
      const source = context.createMediaStreamSource(stream);
      const analyser = context.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      inputAnalyserRef.current = analyser;
      const data = new Uint8Array(analyser.frequencyBinCount);
      const tick = () => {
        analyser.getByteTimeDomainData(data);
        const rms = Math.sqrt(data.reduce((sum, value) => sum + ((value - 128) / 128) ** 2, 0) / data.length);
        setVolume((previous) => Math.min(1, previous * 0.72 + rms * 2.8 * 0.28));
        inputAnimationRef.current = requestAnimationFrame(tick);
      };
      tick();
    } catch {
      // Recording remains functional when Web Audio analysis is unavailable.
    }
  }, []);

  const startOutputMeter = useCallback((audio: HTMLAudioElement) => {
    try {
      const context = new AudioContext();
      const source = context.createMediaElementSource(audio);
      const analyser = context.createAnalyser();
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.78;
      source.connect(analyser);
      analyser.connect(context.destination);
      outputContextRef.current = context;
      outputSourceRef.current = source;
      outputAnalyserRef.current = analyser;
      const data = new Uint8Array(analyser.frequencyBinCount);
      const tick = () => {
        analyser.getByteFrequencyData(data);
        const average = data.reduce((sum, value) => sum + value, 0) / data.length;
        setVolume((previous) => Math.min(1, previous * 0.74 + (average / 128) * 0.26));
        outputAnimationRef.current = requestAnimationFrame(tick);
      };
      tick();
    } catch {
      // Playback remains functional when output analysis is unavailable.
    }
  }, []);

  const speak = useCallback(
    async (text: string) => {
      lastSpokenTextRef.current = text;
      setIsPaused(false);
      setError("");
      stopOutputMeter();
      audioRef.current?.pause();
      audioRef.current = null;
      setState("generating_audio");
      setActiveAction("GENERATING AUDIO · ELEVENLABS");

      try {
        const payload = await api.synthesize(text);
        if (payload.audio_base64) {
          const audio = new Audio(toAudioUrl(payload.audio_base64, payload.audio_format || "mp3"));
          audio.preload = "auto";
          audioRef.current = audio;
          startOutputMeter(audio);
          setState("speaking");
          setActiveAction("SPEAKING · ELEVENLABS");
          await new Promise<void>((resolve, reject) => {
            let settled = false;
            const finish = () => {
              if (settled) return;
              settled = true;
              resolve();
            };
            audio.onended = finish;
            audio.onerror = () => {
              if (settled) return;
              settled = true;
              reject(new Error("David's server voice could not be played."));
            };
            void audio.play().catch((cause) => {
              if (settled) return;
              settled = true;
              reject(cause instanceof Error ? cause : new Error("Browser blocked audio playback."));
            });
          });
          if (audioRef.current === audio) audioRef.current = null;
          stopOutputMeter();
          setState("success");
          setActiveAction("AUDIO COMPLETE · ELEVENLABS");
          return;
        }
        throw new Error(payload.reason || "Server TTS returned no audio.");
      } catch (serverCause) {
        stopOutputMeter();
        audioRef.current = null;
        if (typeof window === "undefined" || !("speechSynthesis" in window)) {
          throw serverCause instanceof Error
            ? serverCause
            : new Error("No voice output is available.");
        }
        window.speechSynthesis.cancel();
        setState("speaking");
        setActiveAction("SPEAKING · BROWSER FALLBACK");
        await new Promise<void>((resolve, reject) => {
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.rate = 0.96;
          utterance.pitch = 0.82;
          utterance.onend = () => resolve();
          utterance.onerror = () => reject(new Error("Browser voice playback failed."));
          window.speechSynthesis.speak(utterance);
        });
        setState("success");
        setActiveAction("AUDIO COMPLETE · BROWSER FALLBACK");
      }
    },
    [startOutputMeter, stopOutputMeter],
  );

  const pause = useCallback(() => {
    if (audioRef.current) audioRef.current.pause();
    if (typeof window !== "undefined" && "speechSynthesis" in window && window.speechSynthesis.speaking) {
      window.speechSynthesis.pause();
    }
    setIsPaused(true);
    setActiveAction("OUTPUT PAUSED");
  }, []);

  const resume = useCallback(() => {
    if (audioRef.current) void audioRef.current.play();
    if (typeof window !== "undefined" && "speechSynthesis" in window && window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
    }
    setIsPaused(false);
    setState("speaking");
    setActiveAction("SPEAKING");
  }, []);

  const replay = useCallback(async () => {
    if (lastSpokenTextRef.current) await speak(lastSpokenTextRef.current);
  }, [speak]);

  const clearTranscript = useCallback(() => {
    setTranscript("");
    setInterimTranscript("");
    setResponse("");
    setError("");
    setActiveAction("STANDBY");
  }, []);

  const processAudio = useCallback(
    async (blob: Blob) => {
      setState("thinking");
      setActiveAction("ANALYZING REQUEST");
      const encoded = await blobToBase64(blob);
      const transcription = await api.transcribe(encoded, "en", blob.type || "audio/webm");
      const text = transcription.text.trim();
      if (!text) throw new Error("No speech was detected. Try speaking closer to the microphone.");
      setTranscript(text);
      setInterimTranscript("");
      setActiveAction("DELEGATING TO SUB-AGENTS");
      const orchestration = await api.orchestrator.process(text, { source: "voice_os", language: transcription.language || "en" });
      const result: VoiceOSResult = {
        transcript: text,
        response: orchestration.text,
        agentsUsed: orchestration.agents_used || [],
        providersUsed: orchestration.providers_used || [],
        planId: orchestration.plan_id,
        taskDetails: orchestration.task_details || [],
      };
      setResponse(orchestration.text);
      setActiveAction(result.agentsUsed.length ? `ASSIGNED: ${result.agentsUsed.join(" · ")}` : "RESPONSE READY");
      options.onResult?.(result);
      await speak(orchestration.text);
    },
    [options, speak],
  );

  const stopListening = useCallback(() => {
    if (recorderRef.current && recorderRef.current.state !== "inactive") recorderRef.current.stop();
    recorderRef.current = null;
    stopStream();
  }, [stopStream]);

  const startListening = useCallback(async () => {
    if (recorderRef.current) return;
    setError("");
    setTranscript("");
    setInterimTranscript("");
    setResponse("");
    setState("listening");
    setActiveAction("LISTENING");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      startInputMeter(stream);
      const recorder = new MediaRecorder(stream, { mimeType: chooseMimeType() });
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onerror = () => {
        const message = "Microphone recording failed.";
        setError(message);
        options.onError?.(message);
        setState("error");
        stopStream();
      };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
        stopStream();
        void processAudio(blob).catch((cause) => {
          const message = cause instanceof Error ? cause.message : "David could not process the voice command.";
          setError(message);
          options.onError?.(message);
          setState("error");
          setActiveAction("VOICE ERROR");
        });
      };
      recorderRef.current = recorder;
      recorder.start();
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "Microphone access is required for voice commands.";
      setError(message);
      options.onError?.(message);
      setState("error");
      setActiveAction("MICROPHONE ACCESS REQUIRED");
      stopStream();
    }
  }, [options, processAudio, startInputMeter, stopStream]);

  const cancel = useCallback(() => {
    if (recorderRef.current && recorderRef.current.state !== "inactive") recorderRef.current.stop();
    recorderRef.current = null;
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.onended = null;
      audioRef.current.onerror = null;
      audioRef.current = null;
    }
    if (typeof window !== "undefined" && "speechSynthesis" in window) window.speechSynthesis.cancel();
    stopOutputMeter();
    stopStream();
    setState("idle");
    setActiveAction("STANDBY");
  }, [stopOutputMeter, stopStream]);

  useEffect(() => () => cancel(), [cancel]);

  return {
    state,
    interimTranscript,
    transcript,
    response,
    activeAction,
    volume,
    error,
    isListening: state === "listening",
    isSpeaking: state === "speaking",
    isGeneratingAudio: state === "generating_audio",
    isPaused,
    pause,
    resume,
    replay,
    clearTranscript,
    toggle: state === "listening" ? stopListening : startListening,
    startListening,
    stopListening,
    cancel,
  };
}
