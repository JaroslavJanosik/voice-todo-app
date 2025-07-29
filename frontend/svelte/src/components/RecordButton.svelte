<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  let isRecording = false;
  let isProcessing = false;
  let mediaRecorder: MediaRecorder;
  let audioChunks: Blob[] = [];

  async function toggleRecording() {
    if (isRecording) {
      // User clicked stop
      mediaRecorder.stop();
    } else {
      // User clicked start
      try {
        audioChunks = [];
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
          // Once recording stops, show spinner
          isProcessing = true;

          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          const formData = new FormData();
          formData.append('file', audioBlob, 'recording.wav');

          try {
            const response = await fetch('http://127.0.0.1:5000/upload', {
              method: 'POST',
              body: formData
            });

            const data = await response.json();
            // Dispatch transcribed text to parent
            if (data.transcription) {
              dispatch('transcribed', { transcription: data.transcription });
            }
          } catch (error) {
            console.error('Error uploading audio:', error);
          } finally {
            // Hide spinner once processing is complete
            isProcessing = false;
            isRecording = false;
          }
        };

        mediaRecorder.start();
        isRecording = true;
      } catch (err) {
        console.error('Error starting recording:', err);
      }
    }
  }
</script>

<button
  on:click={toggleRecording}
  class:is-recording={isRecording}
  disabled={isProcessing}
  aria-label="Toggle Recording"
>
  {#if isProcessing}
    <!-- Show spinner if we're processing -->
    <i class="fas fa-spinner fa-spin"></i>
  {:else if isRecording}
    <!-- Show stop icon if currently recording -->
    <i class="fas fa-stop-circle"></i>
  {:else}
    <!-- Show microphone icon if not recording or processing -->
    <i class="fas fa-microphone"></i>
  {/if}
</button>

<style scoped>
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
  
  button.is-recording i {
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