import { expect, type Page } from '@playwright/test';

export class RecorderComponent {
  constructor(private readonly page: Page) {}

  microphoneSelect() {
    return this.page.getByTestId('microphone-select');
  }

  recordButton() {
    return this.page.getByTestId('record-button');
  }

  async expectReady() {
    await expect(this.recordButton()).toBeVisible();
  }

  async selectInput(label: string) {
    await this.microphoneSelect().selectOption({ label });
  }

  async startRecording() {
    await this.recordButton().click();
  }

  async stopRecording() {
    await this.recordButton().click();
  }
}
