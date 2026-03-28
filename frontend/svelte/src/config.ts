import { env } from '$env/dynamic/public';

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:5000';

type ApiEnvelope<T> = {
  statusCode: number;
  isSuccess: boolean;
  errorMessages: string[];
  result: T;
};

type UploadAudioOptions = {
  language?: string;
  durationMs?: number;
};

export const API_BASE_URL = resolveApiUrl(
  env.PUBLIC_API_BASE_URL,
  typeof window === 'undefined' ? undefined : window.location.origin
);

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  const payload = await readResponsePayload(response);

  if (isApiEnvelope<T>(payload)) {
    if (!response.ok || !payload.isSuccess) {
      throw new Error(extractEnvelopeError(payload, response.status));
    }

    return payload.result;
  }

  if (!response.ok) {
    throw new Error(extractLegacyErrorMessage(payload, response.status));
  }

  return payload as T;
}

export async function uploadAudio(
  blob: Blob,
  filename: string,
  options: UploadAudioOptions = {}
): Promise<{ transcription: string }> {
  const formData = new FormData();
  formData.append('file', blob, filename);

  if (options.language) {
    formData.append('language', options.language);
  }

  if (typeof options.durationMs === 'number' && Number.isFinite(options.durationMs)) {
    formData.append('durationMs', String(Math.max(0, Math.round(options.durationMs))));
  }

  return apiRequest<{ transcription: string }>('/upload', {
    method: 'POST',
    body: formData
  });
}

export function normalizeBaseUrl(value?: string | null) {
  if (!value) {
    return '';
  }

  return value.endsWith('/') ? value.slice(0, -1) : value;
}

export function resolveApiUrl(envValue?: string | null, browserOrigin?: string) {
  const explicitBaseUrl = normalizeBaseUrl(envValue);
  if (explicitBaseUrl) {
    return explicitBaseUrl;
  }

  if (!browserOrigin) {
    return DEFAULT_API_BASE_URL;
  }

  try {
    const currentLocation = new URL(browserOrigin);
    const isLocalHost = currentLocation.hostname === 'localhost' || currentLocation.hostname === '127.0.0.1';
    const isVitePreview = currentLocation.port === '4173';
    const usesDirectDevServer =
      !!currentLocation.port &&
      currentLocation.port !== '80' &&
      currentLocation.port !== '443' &&
      currentLocation.port !== '5000';

    if (isLocalHost && usesDirectDevServer) {
      // Keep browser requests same-origin during Vite dev and let the proxy forward them.
      return isVitePreview ? DEFAULT_API_BASE_URL : '';
    }

    return '';
  } catch {
    return DEFAULT_API_BASE_URL;
  }
}

async function readResponsePayload(response: Response): Promise<unknown> {
  const contentType = response.headers.get('content-type') ?? '';

  if (contentType.includes('application/json')) {
    return response.json();
  }

  const text = await response.text();
  return text ? { error: text } : null;
}

function extractEnvelopeError(payload: ApiEnvelope<unknown>, status: number): string {
  if (Array.isArray(payload.errorMessages) && payload.errorMessages.length > 0) {
    return payload.errorMessages.join(' ');
  }

  return `Request failed with status ${status}.`;
}

function extractLegacyErrorMessage(payload: unknown, status: number): string {
  if (payload && typeof payload === 'object') {
    const error = 'error' in payload ? payload.error : 'message' in payload ? payload.message : null;

    if (typeof error === 'string' && error.trim()) {
      return error;
    }
  }

  return `Request failed with status ${status}.`;
}

function isApiEnvelope<T>(payload: unknown): payload is ApiEnvelope<T> {
  return !!payload && typeof payload === 'object' && 'isSuccess' in payload && 'result' in payload;
}
