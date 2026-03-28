<script lang="ts">
  import { createEventDispatcher, onDestroy } from 'svelte';

  import Icon from '$components/Icon.svelte';
  import { uploadAudio } from '../config';

  type RecordButtonEvents = {
    transcribed: { transcription: string };
    error: { message: string };
  };

  const dispatch = createEventDispatcher<RecordButtonEvents>();

  export let disabled = false;

  let isRecording = false;
  let isProcessing = false;
  let mediaRecorder: MediaRecorder | null = null;
  let mediaStream: MediaStream | null = null;
  let audioChunks: Blob[] = [];
  let recordingMimeType = '';

  onDestroy(() => {
    stopActiveStream();
  });

  async function toggleRecording() {
    if (disabled || isProcessing) {
      return;
    }

    if (isRecording) {
      mediaRecorder?.stop();
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
      dispatchError('Audio recording is not supported in this browser.');
      return;
    }

    try {
      audioChunks = [];
      recordingMimeType = getPreferredMimeType();
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = recordingMimeType
        ? new MediaRecorder(mediaStream, { mimeType: recordingMimeType })
        : new MediaRecorder(mediaStream);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        if (audioChunks.length === 0) {
          stopActiveStream();
          resetState();
          dispatchError('Recording was empty. Please try again.');
          return;
        }

        isProcessing = true;

        const resolvedMimeType = mediaRecorder?.mimeType || recordingMimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunks, { type: resolvedMimeType });
        const extension = getFileExtension(resolvedMimeType);
        try {
          const data = await uploadAudio(audioBlob, `recording.${extension}`);

          if (data?.transcription) {
            dispatch('transcribed', { transcription: data.transcription });
          } else {
            dispatchError('No speech was detected in the recording.');
          }
        } catch (error) {
          dispatchError(getErrorMessage(error, 'Failed to transcribe audio.'));
        } finally {
          stopActiveStream();
          resetState();
        }
      };

      mediaRecorder.start();
      isRecording = true;
    } catch (error) {
      stopActiveStream();
      resetState();
      dispatchError(getRecordingStartError(error));
    }
  }

  function dispatchError(message: string) {
    dispatch('error', { message });
  }

  function stopActiveStream() {
    mediaStream?.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }

  function resetState() {
    audioChunks = [];
    recordingMimeType = '';
    mediaRecorder = null;
    isProcessing = false;
    isRecording = false;
  }

  function getPreferredMimeType() {
    const supportedTypes = ['audio/webm;codecs=opus', 'audio/ogg;codecs=opus', 'audio/mp4'];
    return supportedTypes.find((mimeType) => MediaRecorder.isTypeSupported(mimeType)) ?? '';
  }

  function getFileExtension(mimeType: string) {
    if (mimeType.includes('ogg')) {
      return 'ogg';
    }

    if (mimeType.includes('mp4')) {
      return 'mp4';
    }

    return 'webm';
  }

  function getErrorMessage(error: unknown, fallbackMessage: string) {
    return error instanceof Error ? error.message : fallbackMessage;
  }

  function getRecordingStartError(error: unknown) {
    if (error instanceof DOMException) {
      if (error.name === 'NotAllowedError') {
        return 'Microphone access was denied.';
      }

      if (error.name === 'NotFoundError') {
        return 'No microphone was found on this device.';
      }
    }

    return getErrorMessage(error, 'Unable to start recording.');
  }
</script>

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

<style>
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
</style>
