import { test } from '../fixtures/test-fixtures';
import { buildSuccessEnvelope } from '../support/api-envelope';
import { installMockAudioInput } from '../support/mock-audio';

test.describe('voice capture', () => {
  test('creates a task from a mocked microphone recording', async ({ page, homePage }) => {
    await installMockAudioInput(page, {
      deviceLabel: 'Mock Microphone',
      blobSize: 12_000,
      signalPeak: 0.2,
    });

    await page.route('**/upload', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildSuccessEnvelope(
            {
              transcription: 'Call product designer',
            },
            200
          )
        ),
      });
    });

    await homePage.goto();
    await homePage.expectLoaded();
    await homePage.recorder.expectReady();
    await homePage.recorder.selectInput('Mock Microphone');
    await homePage.recorder.startRecording();
    await page.waitForTimeout(900);
    await homePage.recorder.stopRecording();

    await homePage.expectSuccess('Task added successfully.');
    await homePage.taskList.expectTaskVisible('Call product designer');
    await homePage.expectSummary({
      total: '1',
      active: '1',
      completed: '0',
      completionRate: '0%',
    });
  });
});
