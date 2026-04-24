import io

import pytest
from httpx import AsyncClient


def make_upload_file(content: bytes = b"hello world", filename: str = "test.txt"):
    return ("file", (filename, io.BytesIO(content), "text/plain"))


@pytest.mark.asyncio
class TestFilesAPI:
    async def test_upload_file_success(self, client: AsyncClient, monkeypatch):
        monkeypatch.setattr("src.routers.files.process_file.delay", lambda *a, **kw: None)

        response = await client.post(
            "/files",
            data={"title": "My Test File"},
            files=[make_upload_file()],
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "My Test File"
        assert data["original_name"] == "test.txt"
        assert data["processing_status"] == "uploaded"
        assert data["scan_status"] is None
        assert "id" in data

    async def test_upload_empty_file_returns_400(self, client: AsyncClient, monkeypatch):
        monkeypatch.setattr("src.routers.files.process_file.delay", lambda *a, **kw: None)

        response = await client.post(
            "/files",
            data={"title": "Empty"},
            files=[make_upload_file(content=b"")],
        )

        assert response.status_code == 400

    async def test_upload_without_title_returns_422(self, client: AsyncClient):
        response = await client.post("/files", files=[make_upload_file()])
        assert response.status_code == 422

    async def test_upload_without_file_returns_422(self, client: AsyncClient):
        response = await client.post("/files", data={"title": "No file"})
        assert response.status_code == 422

    async def test_list_files_empty(self, client: AsyncClient):
        response = await client.get("/files")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_files_returns_uploaded(self, client: AsyncClient, monkeypatch):
        monkeypatch.setattr("src.routers.files.process_file.delay", lambda *a, **kw: None)

        await client.post(
            "/files",
            data={"title": "Listed File"},
            files=[make_upload_file(filename="listed.txt")],
        )

        response = await client.get("/files")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "Listed File"

    async def test_get_file_by_id(self, client: AsyncClient, monkeypatch):
        monkeypatch.setattr("src.routers.files.process_file.delay", lambda *a, **kw: None)

        upload = await client.post(
            "/files",
            data={"title": "Specific"},
            files=[make_upload_file()],
        )
        file_id = upload.json()["id"]

        response = await client.get(f"/files/{file_id}")
        assert response.status_code == 200
        assert response.json()["id"] == file_id

    async def test_get_nonexistent_file_returns_404(self, client: AsyncClient):
        response = await client.get("/files/nonexistent-uuid")
        assert response.status_code == 404

    async def test_update_file_title(self, client: AsyncClient, monkeypatch):
        monkeypatch.setattr("src.routers.files.process_file.delay", lambda *a, **kw: None)

        upload = await client.post(
            "/files",
            data={"title": "Old Title"},
            files=[make_upload_file()],
        )
        file_id = upload.json()["id"]

        response = await client.patch(f"/files/{file_id}", json={"title": "New Title"})
        assert response.status_code == 200
        assert response.json()["title"] == "New Title"

    async def test_update_nonexistent_returns_404(self, client: AsyncClient):
        response = await client.patch("/files/nonexistent", json={"title": "New"})
        assert response.status_code == 404

    async def test_update_with_empty_title_returns_422(self, client: AsyncClient, monkeypatch):
        monkeypatch.setattr("src.routers.files.process_file.delay", lambda *a, **kw: None)

        upload = await client.post(
            "/files",
            data={"title": "Valid"},
            files=[make_upload_file()],
        )
        file_id = upload.json()["id"]

        response = await client.patch(f"/files/{file_id}", json={"title": ""})
        assert response.status_code == 422

    async def test_delete_file(self, client: AsyncClient, monkeypatch):
        monkeypatch.setattr("src.routers.files.process_file.delay", lambda *a, **kw: None)

        upload = await client.post(
            "/files",
            data={"title": "To Delete"},
            files=[make_upload_file()],
        )
        file_id = upload.json()["id"]

        assert (await client.delete(f"/files/{file_id}")).status_code == 204
        assert (await client.get(f"/files/{file_id}")).status_code == 404

    async def test_delete_nonexistent_returns_404(self, client: AsyncClient):
        response = await client.delete("/files/nonexistent")
        assert response.status_code == 404

    async def test_download_file(self, client: AsyncClient, monkeypatch):
        monkeypatch.setattr("src.routers.files.process_file.delay", lambda *a, **kw: None)

        content = b"Hello, download test!"
        upload = await client.post(
            "/files",
            data={"title": "Downloadable"},
            files=[make_upload_file(content=content)],
        )
        file_id = upload.json()["id"]

        response = await client.get(f"/files/{file_id}/download")
        assert response.status_code == 200
        assert response.content == content
