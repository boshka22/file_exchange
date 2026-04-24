"use client";

import { Alert, Badge, Card, Col, Container, Row } from "react-bootstrap";
import { useEffect, useState } from "react";

import { AlertsTable } from "@/components/AlertsTable";
import { FileTable } from "@/components/FileTable";
import { PageHeader } from "@/components/PageHeader";
import { UploadModal } from "@/components/UploadModal";
import { useAlerts } from "@/hooks/useAlerts";
import { useFiles } from "@/hooks/useFiles";

export default function Page() {
  const [showModal, setShowModal] = useState(false);

  const {
    files,
    isLoading: filesLoading,
    error: filesError,
    refresh: refreshFiles,
    upload,
    remove,
  } = useFiles();

  const {
    alerts,
    isLoading: alertsLoading,
    error: alertsError,
    refresh: refreshAlerts,
  } = useAlerts();

  useEffect(() => {
    void refreshFiles();
    void refreshAlerts();
  }, [refreshFiles, refreshAlerts]);

  async function handleRefresh() {
    await Promise.all([refreshFiles(), refreshAlerts()]);
  }

  async function handleUpload(title: string, file: File) {
    await upload(title, file);
    void refreshAlerts();
  }

  const globalError = filesError ?? alertsError;

  return (
    <Container fluid className="py-4 px-4 bg-light min-vh-100">
      <Row className="justify-content-center">
        <Col xxl={10} xl={11}>
          <PageHeader
            onRefresh={() => void handleRefresh()}
            onUpload={() => setShowModal(true)}
          />

          {globalError && (
            <Alert variant="danger" className="shadow-sm">
              {globalError}
            </Alert>
          )}

          <Card className="shadow-sm border-0 mb-4">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Файлы</h2>
                <Badge bg="secondary">{files.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <FileTable
                files={files}
                isLoading={filesLoading}
                onDelete={remove}
              />
            </Card.Body>
          </Card>

          <Card className="shadow-sm border-0">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Алерты</h2>
                <Badge bg="secondary">{alerts.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <AlertsTable alerts={alerts} isLoading={alertsLoading} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <UploadModal
        show={showModal}
        onHide={() => setShowModal(false)}
        onUpload={handleUpload}
      />
    </Container>
  );
}
