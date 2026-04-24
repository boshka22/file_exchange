"use client";

import { Badge, Spinner, Table } from "react-bootstrap";

import { formatDate, getAlertLevelVariant } from "@/lib/utils";
import type { AlertItem } from "@/types";

interface AlertsTableProps {
  alerts: AlertItem[];
  isLoading: boolean;
}

export function AlertsTable({ alerts, isLoading }: AlertsTableProps) {
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
            <th>ID</th>
            <th>File ID</th>
            <th>Уровень</th>
            <th>Сообщение</th>
            <th>Создан</th>
          </tr>
        </thead>
        <tbody>
          {alerts.length === 0 ? (
            <tr>
              <td colSpan={5} className="text-center py-4 text-secondary">
                Алертов пока нет
              </td>
            </tr>
          ) : (
            alerts.map((alert) => (
              <tr key={alert.id}>
                <td>{alert.id}</td>
                <td className="small">{alert.file_id}</td>
                <td>
                  <Badge bg={getAlertLevelVariant(alert.level)}>
                    {alert.level}
                  </Badge>
                </td>
                <td>{alert.message}</td>
                <td>{formatDate(alert.created_at)}</td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
    </div>
  );
}
