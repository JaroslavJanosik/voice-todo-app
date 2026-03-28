import type { Page } from '@playwright/test';

type MockAudioOptions = {
  deviceLabel?: string;
  mimeType?: string;
  blobSize?: number;
  signalPeak?: number;
};

export async function installMockAudioInput(page: Page, options: MockAudioOptions = {}) {
  const {
    deviceLabel = 'Mock Microphone',
    mimeType = 'audio/webm;codecs=opus',
    blobSize = 8192,
    signalPeak = 0.18,
  } = options;

  await page.addInitScript(
    ({ resolvedDeviceLabel, resolvedMimeType, resolvedBlobSize, resolvedSignalPeak }) => {
      const fakeDeviceId = 'mock-audio-input-1';
      const eventTarget = new EventTarget();

      class FakeMediaStreamTrack {
        kind = 'audio';
        label = resolvedDeviceLabel;
        enabled = true;
        muted = false;
        readyState: MediaStreamTrackState = 'live';

        stop() {
          this.readyState = 'ended';
        }
      }

      class FakeMediaStream {
        private readonly track = new FakeMediaStreamTrack();

        getTracks() {
          return [this.track];
        }

        getAudioTracks() {
          return [this.track];
        }

        getVideoTracks() {
          return [];
        }
      }

      Object.defineProperty(navigator, 'mediaDevices', {
        configurable: true,
        value: {
          async getUserMedia() {
            return new FakeMediaStream() as unknown as MediaStream;
          },
          async enumerateDevices() {
            return [
              {
                kind: 'audioinput',
                deviceId: fakeDeviceId,
                groupId: 'mock-group',
                label: resolvedDeviceLabel,
                toJSON() {
                  return this;
                },
              },
            ] as MediaDeviceInfo[];
          },
          addEventListener: eventTarget.addEventListener.bind(eventTarget),
          removeEventListener: eventTarget.removeEventListener.bind(eventTarget),
          dispatchEvent: eventTarget.dispatchEvent.bind(eventTarget),
        },
      });

      class FakeMediaRecorder {
        static isTypeSupported(supportedMimeType: string) {
          return supportedMimeType.includes('audio/');
        }

        mimeType: string;
        state: RecordingState = 'inactive';
        ondataavailable: ((event: BlobEvent) => void) | null = null;
        onerror: ((event: Event) => void) | null = null;
        onstop: ((event: Event) => void) | null = null;

        constructor(_stream: MediaStream, mediaRecorderOptions?: MediaRecorderOptions) {
          this.mimeType = mediaRecorderOptions?.mimeType || resolvedMimeType;
        }

        start() {
          this.state = 'recording';
        }

        requestData() {
          this.emitChunk();
        }

        stop() {
          if (this.state === 'inactive') {
            return;
          }

          this.emitChunk();
          this.state = 'inactive';
          this.onstop?.(new Event('stop'));
        }

        private emitChunk() {
          if (!this.ondataavailable) {
            return;
          }

          const payload = new Uint8Array(resolvedBlobSize);
          payload.fill(7);

          this.ondataavailable(
            {
              data: new Blob([payload], { type: this.mimeType }),
            } as BlobEvent
          );
        }
      }

      class FakeAudioContext {
        sampleRate = 44100;
        state: AudioContextState = 'running';

        createMediaStreamSource() {
          return {
            connect() {},
            disconnect() {},
          };
        }

        createGain() {
          return {
            gain: { value: 1 },
            connect() {},
            disconnect() {},
          };
        }

        createScriptProcessor() {
          let intervalId: number | null = null;

          return {
            onaudioprocess: null as ((event: AudioProcessingEvent) => void) | null,
            connect() {
              intervalId = window.setInterval(() => {
                const processor = this as {
                  onaudioprocess: ((event: AudioProcessingEvent) => void) | null;
                };

                processor.onaudioprocess?.({
                  inputBuffer: {
                    getChannelData: () => {
                      const samples = new Float32Array(1024);

                      for (let index = 0; index < samples.length; index += 1) {
                        samples[index] = index % 2 === 0 ? resolvedSignalPeak : -resolvedSignalPeak;
                      }

                      return samples;
                    },
                  },
                } as unknown as AudioProcessingEvent);
              }, 40);
            },
            disconnect() {
              if (intervalId !== null) {
                window.clearInterval(intervalId);
              }
            },
          };
        }

        async resume() {
          this.state = 'running';
        }

        async close() {
          this.state = 'closed';
        }
      }

      Object.defineProperty(window, 'MediaRecorder', {
        configurable: true,
        value: FakeMediaRecorder,
      });
      Object.defineProperty(window, 'AudioContext', {
        configurable: true,
        value: FakeAudioContext,
      });
      Object.defineProperty(window, 'webkitAudioContext', {
        configurable: true,
        value: FakeAudioContext,
      });
    },
    {
      resolvedDeviceLabel: deviceLabel,
      resolvedMimeType: mimeType,
      resolvedBlobSize: blobSize,
      resolvedSignalPeak: signalPeak,
    }
  );
}
