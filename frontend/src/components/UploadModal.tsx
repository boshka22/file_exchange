"use client";

/**
 * Модальное окно загрузки файла.
 *
 * Компонент управляет только своим локальным состоянием формы
 * (title, selectedFile, isSubmitting, error).
 * Логика загрузки делегируется через props.onUpload.
 */

import { type FormEvent, useState } from "react";
import { Alert, Button, Form, Modal } from "react-bootstrap";

interface UploadModalProps {
  show: boolean;
  onHide: () => void;
  onUpload: (title: string, file: File) => Promise<void>;
}

export function UploadModal({ show, onHide, onUpload }: UploadModalProps) {
  const [title, setTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleClose() {
    if (isSubmitting) return;
    setTitle("");
    setSelectedFile(null);
    setError(null);
    onHide();
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!title.trim()) {
      setError("Укажите название файла");
      return;
    }
    if (!selectedFile) {
      setError("Выберите файл для загрузки");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await onUpload(title.trim(), selectedFile);
      handleClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить файл");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Form onSubmit={(e) => void handleSubmit(e)}>
        <Modal.Header closeButton>
          <Modal.Title>Добавить файл</Modal.Title>
        </Modal.Header>

        <Modal.Body>
          {error && (
            <Alert variant="danger" className="mb-3">
              {error}
            </Alert>
          )}

          <Form.Group className="mb-3">
            <Form.Label>Название</Form.Label>
            <Form.Control
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Например, Договор с подрядчиком"
              disabled={isSubmitting}
            />
          </Form.Group>

          <Form.Group>
            <Form.Label>Файл</Form.Label>
            <Form.Control
              type="file"
              onChange={(e) =>
                setSelectedFile(
                  (e.target as HTMLInputElement).files?.[0] ?? null
                )
              }
              disabled={isSubmitting}
            />
          </Form.Group>
        </Modal.Body>

        <Modal.Footer>
          <Button
            variant="outline-secondary"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Отмена
          </Button>
          <Button type="submit" variant="primary" disabled={isSubmitting}>
            {isSubmitting ? "Загрузка..." : "Сохранить"}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
