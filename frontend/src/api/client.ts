import axios from "axios";

/**
 * Single Axios layer for every GWEN backend call.
 * Components must never call fetch/axios inline.
 * Base URL points at the integration-frontend backend mount.
 */
export const api = axios.create({
  baseURL: import.meta.env["VITE_GWEN_API_URL"] ?? "/",
  timeout: 6 * 60 * 1000, // /video/generate-shorts can take 2-5 minutes
});

export const jsonHeaders = { "Content-Type": "application/json" } as const;
export const multipartHeaders = { "Content-Type": "multipart/form-data" } as const;

/** Normalises both error contracts: { error, message } and { detail } */
export function toErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as
      { error?: boolean; message?: string; detail?: string } | undefined;
    if (data?.message) return data.message;
    if (data?.detail) return data.detail;
    if (err.response?.status) return `Request failed with status ${err.response.status}.`;
    return err.message;
  }
  return "Something went wrong. Please try again.";
}
