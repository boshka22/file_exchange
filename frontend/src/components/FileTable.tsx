"use client";

import { Badge, Button, Spinner, Table } from "react-bootstrap";

import { api } from "@/lib/api";
import { formatDate, formatSize, getProcessingVariant } from "@/lib/utils";
import type { FileItem } from "@/types";

interface FileTableProps {
  files: FileItem[];
  isLoading: boolean;
  onDelete: (id: string) => Promise<void>;
}

export function FileTable({ files, isLoading, onDelete }: FileTableProps) {
  if (isLoading) {
    return (
      <div className="d-flex justify-content-center py-5">
        <Spinner animation="border" />
      </div>
    );
  }

  return (
    <div className="table-responsive">
      <Table hover bordered className="align-middle mb-0">
        <thead className="table-light">
          <tr>
            <th>Название</th>
            <th>Файл</th>
            <th>MIME</th>
            <th>Размер</th>
            <th>Статус</th>
            <th>Проверка</th>
            <th>Создан</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {files.length === 0 ? (
            <tr>
              <td colSpan={8} className="text-center py-4 text-secondary">
                Файлы пока не загружены
              </td>
            </tr>
          ) : (
            files.map((file) => (
              <FileRow key={file.id} file={file} onDelete={onDelete} />
            ))
          )}
        </tbody>
      </Table>
    </div>
  );
}

interface FileRowProps {
  file: FileItem;
  onDelete: (id: string) => Promise<void>;
}

function FileRow({ file, onDelete }: FileRowProps) {
  return (
    <tr>
      <td>
        <div className="fw-semibold">{file.title}</div>
        <div className="small text-secondary">{file.id}</div>
      </td>
      <td>{file.original_name}</td>
      <td>{file.mime_type}</td>
      <td>{formatSize(file.size)}</td>
      <td>
        <Badge bg={getProcessingVariant(file.processing_status)}>
          {file.processing_status}
        </Badge>
      </td>
      <td>
        <div className="d-flex flex-column gap-1">
          <Badge bg={file.requires_attention ? "warning" : "success"}>
            {file.scan_status ?? "pending"}
          </Badge>
          <span className="small text-secondary">
            {file.scan_details ?? "Ожидает обработки"}
          </span>
        </div>
      </td>
      <td>{formatDate(file.created_at)}</td>
      <td className="text-nowrap">
        <div className="d-flex gap-2">
          <Button
            as="a"
            href={api.getDownloadUrl(file.id)}
            variant="outline-primary"
            size="sm"
          >
            Скачать
          </Button>
          <Button
            variant="outline-danger"
            size="sm"
            onClick={() => void onDelete(file.id)}
          >
            Удалить
          </Button>
        </div>
      </td>
    </tr>
  );
}
