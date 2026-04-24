"use client";

import { useCallback, useState } from "react";

import { api } from "@/lib/api";
import type { FileItem } from "@/types";

interface UseFilesState {
  files: FileItem[];
  isLoading: boolean;
  error: string | null;
}

interface UseFilesReturn extends UseFilesState {
  refresh: () => Promise<void>;
  upload: (title: string, file: File) => Promise<void>;
  remove: (id: string) => Promise<void>;
}

export function useFiles(): UseFilesReturn {
  const [state, setState] = useState<UseFilesState>({
    files: [],
    isLoading: true,
    error: null,
  });

  const refresh = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));
    try {
      const files = await api.getFiles();
      setState({ files, isLoading: false, error: null });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Ошибка загрузки файлов";
      setState((prev) => ({ ...prev, isLoading: false, error: message }));
    }
  }, []);

  const upload = useCallback(
    async (title: string, file: File) => {
      await api.uploadFile(title, file);
      await refresh();
    },
    [refresh]
  );

  const remove = useCallback(async (id: string) => {
    await api.deleteFile(id);
    setState((prev) => ({
      ...prev,
      files: prev.files.filter((f) => f.id !== id),
    }));
  }, []);

  return { ...state, refresh, upload, remove };
}
