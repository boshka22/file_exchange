import type { AlertItem, FileItem } from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    ...init,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message = body?.detail ?? `HTTP error ${response.status}`;
    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  getFiles(): Promise<FileItem[]> {
    return request<FileItem[]>("/files");
  },

  getFile(id: string): Promise<FileItem> {
    return request<FileItem>(`/files/${id}`);
  },

  uploadFile(title: string, file: File): Promise<FileItem> {
    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);
    return request<FileItem>("/files", { method: "POST", body: formData });
  },

  updateFile(id: string, title: string): Promise<FileItem> {
    return request<FileItem>(`/files/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
  },

  deleteFile(id: string): Promise<void> {
    return request<void>(`/files/${id}`, { method: "DELETE" });
  },

  getDownloadUrl(id: string): string {
    return `${API_BASE_URL}/files/${id}/download`;
  },

  getAlerts(): Promise<AlertItem[]> {
    return request<AlertItem[]>("/alerts");
  },
};
