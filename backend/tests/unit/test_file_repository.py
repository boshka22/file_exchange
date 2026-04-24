import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StoredFile
from src.repositories.file_repository import FileRepository


def make_stored_file(suffix: str = "") -> StoredFile:
    return StoredFile(
        id=f"test-uuid-{suffix}",
        title=f"Test File {suffix}",
        original_name=f"file{suffix}.txt",
        stored_name=f"test-uuid-{suffix}.txt",
        mime_type="text/plain",
        size=1024,
        processing_status="uploaded",
    )


@pytest.mark.asyncio
class TestFileRepository:
    async def test_get_all_empty(self, session: AsyncSession):
        repo = FileRepository(session)
        assert await repo.get_all() == []

    async def test_create_and_get_by_id(self, session: AsyncSession):
        repo = FileRepository(session)
        created = await repo.create(make_stored_file("a"))

        found = await repo.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.title == "Test File a"

    async def test_get_by_id_returns_none_for_missing(self, session: AsyncSession):
        repo = FileRepository(session)
        assert await repo.get_by_id("nonexistent-id") is None

    async def test_get_all_returns_multiple_files(self, session: AsyncSession):
        repo = FileRepository(session)
        for i in range(3):
            await repo.create(make_stored_file(str(i)))

        assert len(await repo.get_all()) == 3

    async def test_update_changes_title(self, session: AsyncSession):
        repo = FileRepository(session)
        file = await repo.create(make_stored_file("b"))

        file.title = "Updated Title"
        updated = await repo.update(file)

        assert updated.title == "Updated Title"

    async def test_delete_removes_file(self, session: AsyncSession):
        repo = FileRepository(session)
        file = await repo.create(make_stored_file("c"))
        await repo.delete(file)

        assert await repo.get_by_id(file.id) is None

    async def test_get_all_sorted_newest_first(self, session: AsyncSession):
        repo = FileRepository(session)
        first = await repo.create(make_stored_file("first"))
        second = await repo.create(make_stored_file("second"))

        result = await repo.get_all()
        ids = [f.id for f in result]

        assert ids.index(second.id) < ids.index(first.id)
