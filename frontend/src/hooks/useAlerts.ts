"use client";

/**
 * Хук для управления состоянием алертов.
 */

import { useCallback, useState } from "react";

import { api } from "@/lib/api";
import type { AlertItem } from "@/types";

interface UseAlertsReturn {
  alerts: AlertItem[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useAlerts(): UseAlertsReturn {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getAlerts();
      setAlerts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки алертов");
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { alerts, isLoading, error, refresh };
}
