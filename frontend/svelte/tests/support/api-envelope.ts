export type ApiEnvelope<T> = {
  statusCode: number;
  isSuccess: boolean;
  errorMessages: string[];
  result: T;
};

export function buildSuccessEnvelope<T>(result: T, statusCode = 200): ApiEnvelope<T> {
  return {
    statusCode,
    isSuccess: true,
    errorMessages: [],
    result,
  };
}
