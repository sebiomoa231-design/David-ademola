import { useCallback, useEffect, useRef, useState } from "react";

export type OperatorVoiceState = "idle" | "listening" | "transcribing" | "reasoning" | "speaking" | "paused" | "cancelled" | "degraded";
export const OPERATOR_VOICE_STATES = ["idle", "listening", "transcribing", "reasoning", "speaking", "paused", "cancelled", "degraded"] as const satisfies readonly OperatorVoiceState[];
export const isProcessingVoiceState = (state: OperatorVoiceState) => state === "transcribing" || state === "reasoning";
export const beginReasoningVoiceState = (state: OperatorVoiceState): OperatorVoiceState => state === "speaking" || state === "paused" ? state : "reasoning";
export const finishReasoningVoiceState = (state: OperatorVoiceState): OperatorVoiceState => state === "reasoning" ? "idle" : state;

type VoiceDependencies = {
  transcribe: (audioBase64: string) => Promise<string>;
  synthesize: (text: string) => Promise<{ audioBase64: string; audioFormat?: string }>;
  onTranscript: (text: string) => void;
};

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error("David AI Operator could not read the recorded audio."));
    reader.onload = () => {
      const value = String(reader.result ?? "");
      const base64 = value.includes(",") ? value.split(",", 2)[1] : "";
      if (!base64) reject(new Error("David AI Operator received an empty audio recording."));
      else resolve(base64);
    };
    reader.readAsDataURL(blob);
  });
}

function decodedAudioBlob(audioBase64: string, format = "mp3") {
  const binary = window.atob(audioBase64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
  return new Blob([bytes], { type: format === "wav" ? "audio/wav" : "audio/mpeg" });
}

function audioBufferToWav(buffer: AudioBuffer): Blob {
  const samples = buffer.length;
  const channels = Math.min(buffer.numberOfChannels, 2);
  const bytesPerSample = 2;
  const headerSize = 44;
  const output = new ArrayBuffer(headerSize + samples * channels * bytesPerSample);
  const view = new DataView(output);
  const writeText = (offset: number, value: string) => { for (let index = 0; index < value.length; index += 1) view.setUint8(offset + index, value.charCodeAt(index)); };
  writeText(0, "RIFF");
  view.setUint32(4, 36 + samples * channels * bytesPerSample, true);
  writeText(8, "WAVE");
  writeText(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, channels, true);
  view.setUint32(24, buffer.sampleRate, true);
  view.setUint32(28, buffer.sampleRate * channels * bytesPerSample, true);
  view.setUint16(32, channels * bytesPerSample, true);
  view.setUint16(34, 16, true);
  writeText(36, "data");
  view.setUint32(40, samples * channels * bytesPerSample, true);
  const channelData = Array.from({ length: channels }, (_, index) => buffer.getChannelData(index));
  let offset = headerSize;
  for (let sample = 0; sample < samples; sample += 1) {
    for (let channel = 0; channel < channels; channel += 1) {
      const value = Math.max(-1, Math.min(1, channelData[channel][sample]));
      view.setInt16(offset, value < 0 ? value * 0x8000 : value * 0x7fff, true);
      offset += bytesPerSample;
    }
  }
  return new Blob([output], { type: "audio/wav" });
}

async function normalizeRecordingForTranscription(recording: Blob): Promise<Blob> {
  const context = new AudioContext();
  try {
    const source = await recording.arrayBuffer();
    const decoded = await context.decodeAudioData(source.slice(0));
    return audioBufferToWav(decoded);
  } finally {
    await context.close();
  }
}

export function useOperatorVoice({ transcribe, synthesize, onTranscript }: VoiceDependencies) {
  const [state, setState] = useState<OperatorVoiceState>("idle");
  const [amplitude, setAmplitude] = useState(0);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const onTranscriptRef = useRef(onTranscript);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const inputStreamRef = useRef<MediaStream | null>(null);
  const inputContextRef = useRef<AudioContext | null>(null);
  const outputContextRef = useRef<AudioContext | null>(null);
  const animationRef = useRef<number | null>(null);
  const playerRef = useRef<HTMLAudioElement | null>(null);
  const outputUrlRef = useRef<string | null>(null);
  const cancelledTimerRef = useRef<number | null>(null);
  const outputAnalysisReadyRef = useRef(false);

  useEffect(() => { onTranscriptRef.current = onTranscript; }, [onTranscript]);

  const stopAmplitude = useCallback(() => {
    if (animationRef.current !== null) window.cancelAnimationFrame(animationRef.current);
    animationRef.current = null;
    setAmplitude(0);
  }, []);

  const closeInput = useCallback(() => {
    recorderRef.current = null;
    inputStreamRef.current?.getTracks().forEach((track) => track.stop());
    inputStreamRef.current = null;
    void inputContextRef.current?.close();
    inputContextRef.current = null;
  }, []);

  const releaseVoiceOutput = useCallback((nextState: OperatorVoiceState = "idle") => {
    if (cancelledTimerRef.current !== null) window.clearTimeout(cancelledTimerRef.current);
    cancelledTimerRef.current = null;
    const player = playerRef.current;
    if (player) {
      player.pause();
      player.currentTime = 0;
      playerRef.current = null;
    }
    if (outputUrlRef.current) URL.revokeObjectURL(outputUrlRef.current);
    outputUrlRef.current = null;
    void outputContextRef.current?.close();
    outputContextRef.current = null;
    outputAnalysisReadyRef.current = false;
    stopAmplitude();
    setState(nextState);
  }, [stopAmplitude]);

  const cancelSpeaking = useCallback(() => releaseVoiceOutput("idle"), [releaseVoiceOutput]);
  const interruptSpeaking = useCallback(() => {
    releaseVoiceOutput("cancelled");
    cancelledTimerRef.current = window.setTimeout(() => {
      cancelledTimerRef.current = null;
      setState((current) => current === "cancelled" ? "idle" : current);
    }, 1500);
  }, [releaseVoiceOutput]);

  const pauseSpeaking = useCallback(() => {
    const player = playerRef.current;
    if (!player || player.paused) return;
    player.pause();
    stopAmplitude();
    setState("paused");
  }, [stopAmplitude]);

  const resumeSpeaking = useCallback(async () => {
    const player = playerRef.current;
    if (!player) return;
    try {
      await player.play();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "David AI Operator could not resume voice output.");
      setState("degraded");
    }
  }, []);

  const clearTranscript = useCallback(() => setTranscript(""), []);
  const beginReasoning = useCallback(() => {
    setError(null);
    setState(beginReasoningVoiceState);
  }, []);
  const finishReasoning = useCallback(() => {
    setState(finishReasoningVoiceState);
  }, []);

  const stopListening = useCallback(() => {
    const recorder = recorderRef.current;
    if (recorder && recorder.state !== "inactive") recorder.stop();
    else {
      closeInput();
      stopAmplitude();
      setState("idle");
    }
  }, [closeInput, stopAmplitude]);

  const sampleAnalyser = useCallback((analyser: AnalyserNode) => {
    const bins = new Uint8Array(analyser.fftSize);
    const tick = () => {
      analyser.getByteTimeDomainData(bins);
      let energy = 0;
      for (let index = 0; index < bins.length; index += 1) energy += Math.abs(bins[index] - 128) / 128;
      const normalized = Math.min(1, (energy / bins.length) * 3.5);
      setAmplitude((current) => Math.max(normalized, current * 0.78));
      animationRef.current = window.requestAnimationFrame(tick);
    };
    tick();
  }, []);

  const startListening = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setError("This browser does not support microphone recording.");
      setState("degraded");
      return;
    }
    cancelSpeaking();
    setError(null);
    setTranscript("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } });
      inputStreamRef.current = stream;
      const context = new AudioContext();
      inputContextRef.current = context;
      const analyser = context.createAnalyser();
      analyser.fftSize = 512;
      context.createMediaStreamSource(stream).connect(analyser);
      sampleAnalyser(analyser);
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" : "audio/webm";
      const recorder = new MediaRecorder(stream, { mimeType });
      const chunks: BlobPart[] = [];
      recorder.ondataavailable = (event) => { if (event.data.size) chunks.push(event.data); };
      recorder.onstop = async () => {
        closeInput();
        stopAmplitude();
        if (!chunks.length) { setState("idle"); return; }
        setState("transcribing");
        try {
          const wavRecording = await normalizeRecordingForTranscription(new Blob(chunks, { type: mimeType }));
          const audioBase64 = await blobToBase64(wavRecording);
          const text = (await transcribe(audioBase64)).trim();
          if (!text) throw new Error("David AI Operator could not detect speech in that recording.");
          setTranscript(text);
          if (/^(stop|cancel|be quiet|quiet)$/i.test(text.replace(/[.!?]/g, "").trim())) {
            interruptSpeaking();
            return;
          }
          onTranscriptRef.current(text);
          setState("idle");
        } catch (cause) {
          setError(cause instanceof Error ? cause.message : "Speech transcription failed.");
          setState("degraded");
        }
      };
      recorderRef.current = recorder;
      recorder.start();
      setState("listening");
    } catch (cause) {
      const reason = cause instanceof DOMException && cause.name === "NotAllowedError"
        ? "Microphone access is required before David AI Operator can listen."
        : cause instanceof Error ? cause.message : "David AI Operator could not open the microphone.";
      closeInput();
      stopAmplitude();
      setError(reason);
      setState("degraded");
    }
  }, [cancelSpeaking, closeInput, interruptSpeaking, sampleAnalyser, stopAmplitude, transcribe]);

  const speak = useCallback(async (text: string) => {
    const cleanText = text.replace(/\*+/g, "").trim();
    if (!cleanText) return;
    cancelSpeaking();
    setError(null);
    try {
      const result = await synthesize(cleanText);
      const url = URL.createObjectURL(decodedAudioBlob(result.audioBase64, result.audioFormat));
      outputUrlRef.current = url;
      const player = new Audio(url);
      playerRef.current = player;
      player.onplay = () => {
        setState("speaking");
        if (outputAnalysisReadyRef.current) return;
        try {
          const context = new AudioContext();
          outputContextRef.current = context;
          const analyser = context.createAnalyser();
          analyser.fftSize = 512;
          const source = context.createMediaElementSource(player);
          source.connect(analyser);
          analyser.connect(context.destination);
          sampleAnalyser(analyser);
          outputAnalysisReadyRef.current = true;
        } catch {
          setAmplitude(0.22);
        }
      };
      player.onended = () => cancelSpeaking();
      player.onerror = () => { setError("David AI Operator could not play the returned voice audio."); setState("degraded"); };
      await player.play();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Speech output failed.");
      setState("degraded");
    }
  }, [cancelSpeaking, sampleAnalyser, synthesize]);

  useEffect(() => () => { stopListening(); cancelSpeaking(); }, [cancelSpeaking, stopListening]);

  return { state, amplitude, transcript, error, startListening, stopListening, cancelSpeaking, interruptSpeaking, pauseSpeaking, resumeSpeaking, clearTranscript, beginReasoning, finishReasoning, speak, isSupported: typeof window !== "undefined" && Boolean(navigator.mediaDevices?.getUserMedia) };
}
