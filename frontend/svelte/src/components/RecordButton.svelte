<script lang="ts">
  import { createEventDispatcher, onDestroy, onMount } from 'svelte';

  import Icon from '$components/Icon.svelte';
  import { startAudioRecording, type AudioRecorderSession, type AudioRecordingResult } from '$lib/audioRecorder';
  import { uploadAudio } from '../config';

  type RecordButtonEvents = {
    transcribed: { transcription: string };
    error: { message: string };
  };

  const dispatch = createEventDispatcher<RecordButtonEvents>();
  const MIN_RECORDING_DURATION_MS = 700;
  const MIN_SIGNAL_PEAK = 0.003;
  const MICROPHONE_STORAGE_KEY = 'voice-todo-preferred-microphone';

  export let disabled = false;

  let isRecording = false;
  let isProcessing = false;
  let recordingSession: AudioRecorderSession | null = null;
  let audioDevices: MediaDeviceInfo[] = [];
  let selectedDeviceId = '';
  let audioLevel = 0;

  onMount(() => {
    void loadAudioDevices();
    navigator.mediaDevices?.addEventListener?.('devicechange', handleDeviceChange);
  });

  onDestroy(() => {
    void recordingSession?.cancel();
    navigator.mediaDevices?.removeEventListener?.('devicechange', handleDeviceChange);
  });

  async function toggleRecording() {
    if (disabled || isProcessing) {
      return;
    }

    if (isRecording) {
      await stopRecording();
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      dispatchError('Audio recording is not supported in this browser.');
      return;
    }

    try {
      recordingSession = await startAudioRecording({
        deviceId: selectedDeviceId || undefined,
        onLevelChange: handleLevelChange
      });
      isRecording = true;
      await loadAudioDevices();
    } catch (error) {
      resetState();
      dispatchError(getRecordingStartError(error));
    }
  }

  async function stopRecording() {
    const activeSession = recordingSession;
    if (!activeSession) {
      return;
    }

    isProcessing = true;
    isRecording = false;
    recordingSession = null;

    try {
      const recording = await activeSession.stop();

      if (recording.durationMs < MIN_RECORDING_DURATION_MS) {
        dispatchError('Recording was too short. Please speak for a little longer.');
        return;
      }

      if (recording.blob.size === 0) {
        dispatchError('Recording was empty. Please try again.');
        return;
      }

      if (recording.peakAmplitude !== null && recording.peakAmplitude < MIN_SIGNAL_PEAK) {
        dispatchError('No microphone signal was detected. Check the selected input device and browser microphone permission.');
        return;
      }

      const filename = getFileNameForRecording(recording);
      const data = await uploadAudio(recording.blob, filename, {
        language: getPreferredTranscriptionLanguage(),
        durationMs: recording.durationMs
      });

      if (data?.transcription) {
        dispatch('transcribed', { transcription: data.transcription });
      } else {
        dispatchError('No speech was detected in the recording. Please try again.');
      }
    } catch (error) {
      dispatchError(getUploadErrorMessage(error));
    } finally {
      resetState();
    }
  }

  function dispatchError(message: string) {
    dispatch('error', { message });
  }

  function resetState() {
    recordingSession = null;
    isProcessing = false;
    isRecording = false;
    audioLevel = 0;
  }

  function getFileNameForRecording(recording: AudioRecordingResult) {
    if (recording.mimeType.includes('ogg')) {
      return 'recording.ogg';
    }

    if (recording.mimeType.includes('mp4')) {
      return 'recording.mp4';
    }

    if (recording.mimeType.includes('wav')) {
      return 'recording.wav';
    }

    return 'recording.webm';
  }

  function getPreferredTranscriptionLanguage() {
    return typeof navigator.language === 'string' ? navigator.language : '';
  }

  function getErrorMessage(error: unknown, fallbackMessage: string) {
    return error instanceof Error ? error.message : fallbackMessage;
  }

  function getUploadErrorMessage(error: unknown) {
    const message = getErrorMessage(error, 'Failed to transcribe audio.');

    if (message.includes('No speech detected in the uploaded audio.')) {
      return 'No speech was detected in the recording. Please speak a little longer or closer to the microphone.';
    }

    return message;
  }

  function getRecordingStartError(error: unknown) {
    if (error instanceof DOMException) {
      if (error.name === 'NotAllowedError') {
        return 'Microphone access was denied.';
      }

      if (error.name === 'NotFoundError') {
        return 'No microphone was found on this device.';
      }

      if (error.name === 'NotReadableError') {
        return 'The selected microphone is busy or unavailable. Try another input device.';
      }

      if (error.name === 'OverconstrainedError') {
        return 'The selected microphone is no longer available. Choose another input device.';
      }
    }

    return getErrorMessage(error, 'Unable to start recording.');
  }

  async function loadAudioDevices() {
    if (!navigator.mediaDevices?.enumerateDevices) {
      return;
    }

    const devices = (await navigator.mediaDevices.enumerateDevices()).filter(
      (device) => device.kind === 'audioinput'
    );

    audioDevices = devices;

    if (devices.length === 0) {
      selectedDeviceId = '';
      return;
    }

    const storedDeviceId = getStoredDeviceId();
    const preferredDeviceId = storedDeviceId || selectedDeviceId;
    const hasPreferredDevice = preferredDeviceId && devices.some((device) => device.deviceId === preferredDeviceId);
    selectedDeviceId = hasPreferredDevice ? preferredDeviceId : devices[0].deviceId;
    storeDeviceId(selectedDeviceId);
  }

  function handleDeviceChange() {
    void loadAudioDevices();
  }

  function handleSelectedDeviceChange(event: Event) {
    const target = event.currentTarget as HTMLSelectElement;
    selectedDeviceId = target.value;
    storeDeviceId(selectedDeviceId);
  }

  function handleLevelChange(level: number) {
    audioLevel = Math.min(1, level * 10);
  }

  function getStoredDeviceId() {
    if (typeof localStorage === 'undefined') {
      return '';
    }

    return localStorage.getItem(MICROPHONE_STORAGE_KEY) ?? '';
  }

  function storeDeviceId(deviceId: string) {
    if (typeof localStorage === 'undefined') {
      return;
    }

    localStorage.setItem(MICROPHONE_STORAGE_KEY, deviceId);
  }

  function getDeviceLabel(device: MediaDeviceInfo, index: number) {
    return device.label || `Microphone ${index + 1}`;
  }
</script>

<div class="recorder">
  {#if audioDevices.length > 0}
    <label class="device-picker">
      <span>Input</span>
      <select
        value={selectedDeviceId}
        on:change={handleSelectedDeviceChange}
        disabled={disabled || isProcessing || isRecording}
        data-cy="microphone-select"
      >
        {#each audioDevices as device, index}
          <option value={device.deviceId}>{getDeviceLabel(device, index)}</option>
        {/each}
      </select>
    </label>
  {/if}

  <button
    on:click={toggleRecording}
    class:is-recording={isRecording}
    disabled={disabled || isProcessing}
    aria-label="Toggle Recording"
    aria-busy={isProcessing}
    data-cy="record-button"
  >
    {#if isProcessing}
      <Icon name="spinner" className="spinner" />
    {:else if isRecording}
      <Icon name="stop" />
    {:else}
      <Icon name="microphone" />
    {/if}
  </button>

  <div class="level-meter" aria-hidden="true">
    <div class="level-track">
      <span class="level-fill" style={`transform: scaleX(${audioLevel})`}></span>
    </div>
  </div>
</div>

<style>
  .recorder {
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: center;
  }

  .device-picker {
    width: min(100%, 320px);
    display: flex;
    flex-direction: column;
    gap: 6px;
    text-align: left;
    font-size: 12px;
    opacity: 0.92;
  }

  .device-picker span {
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .device-picker select {
    width: 100%;
    border: 1px solid rgba(255, 255, 255, 0.18);
    background: rgba(255, 255, 255, 0.12);
    color: white;
    border-radius: 12px;
    padding: 10px 12px;
    outline: none;
  }

  .device-picker select:disabled {
    opacity: 0.65;
  }

  button {
    width: 60px;
    height: 60px;
    border: none;
    border-radius: 50%;
    background: white;
    color: black;
    font-size: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.3s ease-in-out, transform 0.2s;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    margin: 0 auto;
  }

  button :global(svg) {
    width: 26px;
    height: 26px;
  }

  button.is-recording {
    color: #764ba2;
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  button:hover:enabled {
    transform: scale(1.1);
    box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.3);
  }

  .level-meter {
    width: min(100%, 220px);
  }

  .level-track {
    width: 100%;
    height: 10px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.18);
    overflow: hidden;
  }

  .level-fill {
    display: block;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, #9be15d 0%, #00e3ae 100%);
    transform-origin: left center;
    transition: transform 80ms linear;
  }
</style>
