"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, toAudioUrl } from "@/lib/api";

export type VoiceOSState = "idle" | "listening" | "thinking" | "speaking" | "error";

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
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationRef = useRef<number | null>(null);

  const stopMeter = useCallback(() => {
    if (animationRef.current !== null) cancelAnimationFrame(animationRef.current);
    animationRef.current = null;
    setVolume(0);
  }, []);

  const stopStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    analyserRef.current?.disconnect();
    analyserRef.current = null;
    stopMeter();
  }, [stopMeter]);

  const startMeter = useCallback((stream: MediaStream) => {
    try {
      const context = new AudioContext();
      const source = context.createMediaStreamSource(stream);
      const analyser = context.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;
      const data = new Uint8Array(analyser.frequencyBinCount);
      const tick = () => {
        analyser.getByteTimeDomainData(data);
        const rms = Math.sqrt(data.reduce((sum, value) => sum + ((value - 128) / 128) ** 2, 0) / data.length);
        setVolume((previous) => Math.min(1, previous * 0.72 + rms * 2.8 * 0.28));
        animationRef.current = requestAnimationFrame(tick);
      };
      tick();
    } catch {
      // The recorder remains functional if Web Audio analysis is unavailable.
    }
  }, []);

  const speak = useCallback(async (text: string) => {
    const payload = await api.synthesize(text);
    if (!payload.audio_base64) {
      setState("idle");
      return;
    }
    const audio = new Audio(toAudioUrl(payload.audio_base64, payload.audio_format || "mp3"));
    audioRef.current = audio;
    setState("speaking");
    setActiveAction("RESPONSE READY");
    await new Promise<void>((resolve, reject) => {
      audio.onended = () => resolve();
      audio.onerror = () => reject(new Error("David's voice output could not be played."));
      void audio.play().catch(reject);
    });
    audioRef.current = null;
    setState("idle");
    setActiveAction("STANDBY");
  }, []);

  const processAudio = useCallback(async (blob: Blob) => {
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
  }, [options, speak]);

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
      startMeter(stream);
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
  }, [options, processAudio, startMeter, stopStream]);

  const cancel = useCallback(() => {
    if (recorderRef.current && recorderRef.current.state !== "inactive") recorderRef.current.stop();
    recorderRef.current = null;
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    stopStream();
    setState("idle");
    setActiveAction("STANDBY");
  }, [stopStream]);

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
    toggle: state === "listening" ? stopListening : startListening,
    startListening,
    stopListening,
    cancel,
  };
}
