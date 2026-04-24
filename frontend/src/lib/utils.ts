import type { AlertLevel, ProcessingStatus } from "@/types";

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

export function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function getAlertLevelVariant(
  level: AlertLevel | string
): "danger" | "warning" | "success" {
  if (level === "critical") return "danger";
  if (level === "warning") return "warning";
  return "success";
}

export function getProcessingVariant(
  status: ProcessingStatus | string
): "danger" | "warning" | "success" | "secondary" {
  if (status === "failed") return "danger";
  if (status === "processing") return "warning";
  if (status === "processed") return "success";
  return "secondary";
}
