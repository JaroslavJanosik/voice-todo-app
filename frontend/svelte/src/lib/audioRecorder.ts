export type AudioRecordingResult = {
  blob: Blob;
  durationMs: number;
  mimeType: string;
  source: 'media-recorder' | 'pcm-fallback';
  peakAmplitude: number | null;
};

export type AudioRecorderSession = {
  stop: () => Promise<AudioRecordingResult>;
  cancel: () => Promise<void>;
};

export type StartAudioRecordingOptions = {
  deviceId?: string;
  onLevelChange?: (level: number) => void;
};

type MediaCaptureResult = {
  blob: Blob;
  mimeType: string;
  source: 'media-recorder';
};

type PcmCaptureResult = {
  blob: Blob;
  mimeType: 'audio/wav';
  source: 'pcm-fallback';
  peakAmplitude: number;
};

const SCRIPT_PROCESSOR_BUFFER_SIZE = 4096;
const MEDIA_RECORDER_TIMESLICE_MS = 250;
const MIN_USEFUL_MEDIA_BYTES_PER_SECOND = 800;

export async function startAudioRecording(options: StartAudioRecordingOptions = {}): Promise<AudioRecorderSession> {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error('Audio recording is not supported in this browser.');
  }

  const audioConstraints: MediaTrackConstraints = {
    channelCount: { ideal: 1 },
    echoCancellation: { ideal: true },
    noiseSuppression: { ideal: true },
    autoGainControl: { ideal: true }
  };

  if (options.deviceId) {
    audioConstraints.deviceId = { exact: options.deviceId };
  }

  const stream = await navigator.mediaDevices.getUserMedia({
    audio: audioConstraints
  });

  const mediaCapture = createMediaRecorderCapture(stream);
  const pcmCapture = createPcmCapture(stream, options.onLevelChange);

  if (!mediaCapture && !pcmCapture) {
    stream.getTracks().forEach((track) => track.stop());
    throw new Error('Audio recording is not supported in this browser.');
  }

  const startedAt = Date.now();
  let finalized = false;

  async function finalize() {
    if (finalized) {
      return;
    }

    finalized = true;
    stream.getTracks().forEach((track) => track.stop());
  }

  return {
    async stop() {
      try {
        const [mediaResult, pcmResult] = await Promise.all([
          mediaCapture?.stop() ?? Promise.resolve(null),
          pcmCapture?.stop() ?? Promise.resolve(null)
        ]);

        const durationMs = Date.now() - startedAt;
        return pickRecordingResult(mediaResult, pcmResult, durationMs);
      } finally {
        await finalize();
      }
    },
    async cancel() {
      try {
        await Promise.all([
          mediaCapture?.cancel() ?? Promise.resolve(),
          pcmCapture?.cancel() ?? Promise.resolve()
        ]);
      } finally {
        await finalize();
      }
    }
  };
}

function createMediaRecorderCapture(stream: MediaStream) {
  if (typeof MediaRecorder === 'undefined') {
    return null;
  }

  const preferredMimeType = getPreferredMediaRecorderMimeType();
  let mediaRecorder: MediaRecorder;

  try {
    mediaRecorder = preferredMimeType
      ? new MediaRecorder(stream, { mimeType: preferredMimeType, audioBitsPerSecond: 128000 })
      : new MediaRecorder(stream);
  } catch {
    return null;
  }

  const chunks: Blob[] = [];
  const resultPromise = new Promise<MediaCaptureResult | null>((resolve, reject) => {
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    mediaRecorder.onerror = () => {
      reject(new Error('Recording failed. Please try again.'));
    };

    mediaRecorder.onstop = () => {
      const mimeType = mediaRecorder.mimeType || preferredMimeType || 'audio/webm';
      resolve({
        blob: new Blob(chunks, { type: mimeType }),
        mimeType,
        source: 'media-recorder'
      });
    };
  });

  mediaRecorder.start(MEDIA_RECORDER_TIMESLICE_MS);

  return {
    async stop() {
      if (mediaRecorder.state !== 'inactive') {
        try {
          mediaRecorder.requestData();
        } catch {
          // Some browsers do not support requestData reliably.
        }

        mediaRecorder.stop();
      }

      return resultPromise;
    },
    async cancel() {
      if (mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
      }

      await resultPromise.catch(() => null);
    }
  };
}

function createPcmCapture(stream: MediaStream, onLevelChange?: (level: number) => void) {
  const AudioContextConstructor = getAudioContextConstructor();
  if (!AudioContextConstructor) {
    return null;
  }

  const audioContext = new AudioContextConstructor();
  const sampleRate = audioContext.sampleRate;
  const source = audioContext.createMediaStreamSource(stream);
  const processor = audioContext.createScriptProcessor(SCRIPT_PROCESSOR_BUFFER_SIZE, 1, 1);
  const mutedOutput = audioContext.createGain();
  const chunks: Float32Array[] = [];

  let totalSamples = 0;
  let peakAmplitude = 0;
  let closed = false;

  mutedOutput.gain.value = 0;

  processor.onaudioprocess = (event) => {
    const inputChannel = event.inputBuffer.getChannelData(0);
    const copy = new Float32Array(inputChannel.length);
    copy.set(inputChannel);
    chunks.push(copy);
    totalSamples += copy.length;
    let chunkPeakAmplitude = 0;

    for (let index = 0; index < copy.length; index += 1) {
      const amplitude = Math.abs(copy[index]);
      if (amplitude > chunkPeakAmplitude) {
        chunkPeakAmplitude = amplitude;
      }
      if (amplitude > peakAmplitude) {
        peakAmplitude = amplitude;
      }
    }

    onLevelChange?.(chunkPeakAmplitude);
  };

  source.connect(processor);
  processor.connect(mutedOutput);
  mutedOutput.connect(audioContext.destination);

  const ready = audioContext.state === 'suspended' ? audioContext.resume() : Promise.resolve();

  async function close() {
    if (closed) {
      return;
    }

    closed = true;
    processor.disconnect();
    mutedOutput.disconnect();
    source.disconnect();
    onLevelChange?.(0);

    if (audioContext.state !== 'closed') {
      await audioContext.close();
    }
  }

  return {
    async stop() {
      await ready;
      const blob = encodeWav(chunks, totalSamples, sampleRate);
      await close();

      return {
        blob,
        mimeType: 'audio/wav' as const,
        source: 'pcm-fallback' as const,
        peakAmplitude
      };
    },
    async cancel() {
      await close();
    }
  };
}

function pickRecordingResult(
  mediaResult: MediaCaptureResult | null,
  pcmResult: PcmCaptureResult | null,
  durationMs: number
): AudioRecordingResult {
  const peakAmplitude = pcmResult?.peakAmplitude ?? null;

  if (mediaResult && isUsefulMediaRecording(mediaResult.blob.size, durationMs)) {
    return {
      ...mediaResult,
      durationMs,
      peakAmplitude
    };
  }

  if (pcmResult && pcmResult.blob.size > 44) {
    return {
      ...pcmResult,
      durationMs
    };
  }

  if (mediaResult) {
    return {
      ...mediaResult,
      durationMs,
      peakAmplitude
    };
  }

  if (pcmResult) {
    return {
      ...pcmResult,
      durationMs
    };
  }

  throw new Error('Recording was empty. Please try again.');
}

function isUsefulMediaRecording(size: number, durationMs: number) {
  const minimumExpectedSize = Math.max(2048, Math.floor((durationMs / 1000) * MIN_USEFUL_MEDIA_BYTES_PER_SECOND));
  return size >= minimumExpectedSize;
}

function getPreferredMediaRecorderMimeType() {
  const supportedTypes = [
    'audio/webm;codecs=opus',
    'audio/ogg;codecs=opus',
    'audio/mp4',
    'audio/webm'
  ];

  return supportedTypes.find((mimeType) => MediaRecorder.isTypeSupported(mimeType)) ?? '';
}

function getAudioContextConstructor() {
  if (typeof window === 'undefined') {
    return null;
  }

  return (
    window.AudioContext ??
    (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext ??
    null
  );
}

function encodeWav(chunks: Float32Array[], totalSamples: number, sampleRate: number) {
  const samples = mergeChunks(chunks, totalSamples);
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);

  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(view, 36, 'data');
  view.setUint32(40, samples.length * 2, true);
  writePcmSamples(view, 44, samples);

  return new Blob([view], { type: 'audio/wav' });
}

function mergeChunks(chunks: Float32Array[], totalSamples: number) {
  const result = new Float32Array(totalSamples);
  let offset = 0;

  for (const chunk of chunks) {
    result.set(chunk, offset);
    offset += chunk.length;
  }

  return result;
}

function writePcmSamples(view: DataView, offset: number, samples: Float32Array) {
  let writeOffset = offset;

  for (let index = 0; index < samples.length; index += 1) {
    const value = Math.max(-1, Math.min(1, samples[index]));
    const sample = value < 0 ? value * 0x8000 : value * 0x7fff;
    view.setInt16(writeOffset, sample, true);
    writeOffset += 2;
  }
}

function writeString(view: DataView, offset: number, value: string) {
  for (let index = 0; index < value.length; index += 1) {
    view.setUint8(offset + index, value.charCodeAt(index));
  }
}
