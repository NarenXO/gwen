import { api, multipartHeaders } from "./client";

export interface VideoAnalyzeResponse {
  [key: string]: unknown;
}

export interface ThumbnailAnalyzeResponse {
  [key: string]: unknown;
}

export interface GenerateShortsResponse {
  [key: string]: unknown;
}

function formData(file: File, field = "file") {
  const fd = new FormData();
  fd.append(field, file);
  return fd;
}

export async function analyzeVideo(file: File) {
  const { data } = await api.post<VideoAnalyzeResponse>("/video/analyze", formData(file), {
    headers: multipartHeaders,
  });
  return data;
}

export async function analyzeThumbnail(file: File) {
  const { data } = await api.post<ThumbnailAnalyzeResponse>("/thumbnail/analyze", formData(file), {
    headers: multipartHeaders,
  });
  return data;
}

/** Synchronous but slow: 2-5 minutes. Caller must show a real waiting state. */
export async function generateShorts(file: File) {
  const { data } = await api.post<GenerateShortsResponse>(
    "/video/generate-shorts",
    formData(file),
    { headers: multipartHeaders },
  );
  return data;
}

export function downloadUrl(filename: string) {
  const base = (api.defaults.baseURL ?? "/").replace(/\/$/, "");
  return `${base}/video/download/${encodeURIComponent(filename)}`;
}
