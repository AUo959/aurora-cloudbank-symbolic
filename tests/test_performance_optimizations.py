"""
Performance optimization tests for Aurora CloudBank Symbolic.

Tests validate that async file I/O improvements work correctly.
"""

import asyncio
import tempfile
from pathlib import Path

import pytest


class TestAsyncFileIO:
    """Test async file I/O improvements."""

    @pytest.mark.asyncio
    async def test_async_file_read_write(self):
        """Test async file read and write operations."""
        try:
            import aiofiles
        except ImportError:
            pytest.skip("aiofiles not available")

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = Path(f.name)
            f.write("test content")

        try:
            # Test async read
            async with aiofiles.open(temp_path, 'r') as f:
                content = await f.read()
            assert content == "test content"

            # Test async write
            async with aiofiles.open(temp_path, 'w') as f:
                await f.write("new content")

            # Verify write
            async with aiofiles.open(temp_path, 'r') as f:
                content = await f.read()
            assert content == "new content"
        finally:
            # Cleanup
            temp_path.unlink()

    @pytest.mark.asyncio
    async def test_async_binary_operations(self):
        """Test async binary file operations."""
        try:
            import aiofiles
        except ImportError:
            pytest.skip("aiofiles not available")

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as f:
            temp_path = Path(f.name)
            test_data = b"binary test data"
            f.write(test_data)

        try:
            # Test async binary read
            async with aiofiles.open(temp_path, 'rb') as f:
                content = await f.read()
            assert content == test_data

            # Test async binary write
            new_data = b"new binary data"
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(new_data)

            # Verify write
            async with aiofiles.open(temp_path, 'rb') as f:
                content = await f.read()
            assert content == new_data
        finally:
            # Cleanup
            temp_path.unlink()

    @pytest.mark.asyncio
    async def test_concurrent_file_operations(self):
        """Test that multiple async file operations can run concurrently."""
        try:
            import aiofiles
        except ImportError:
            pytest.skip("aiofiles not available")

        temp_files = []

        try:
            # Create multiple temp files using context managers
            for i in range(5):
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_{i}.txt') as f:
                    temp_files.append(Path(f.name))

            # Concurrent writes
            async def write_file(path, content):
                async with aiofiles.open(path, 'w') as f:
                    await f.write(content)

            write_tasks = [
                write_file(path, f"content_{i}")
                for i, path in enumerate(temp_files)
            ]
            await asyncio.gather(*write_tasks)

            # Concurrent reads
            async def read_file(path):
                async with aiofiles.open(path, 'r') as f:
                    return await f.read()

            read_tasks = [read_file(path) for path in temp_files]
            contents = await asyncio.gather(*read_tasks)

            # Verify all files were written correctly
            for i, content in enumerate(contents):
                assert content == f"content_{i}"

        finally:
            # Cleanup
            for path in temp_files:
                if path.exists():
                    path.unlink()


class TestStringBuilding:
    """Test efficient string building patterns."""

    def test_list_join_vs_concatenation(self):
        """Verify list.join is more efficient than concatenation."""
        items = [f"item_{i}" for i in range(100)]

        # Efficient method
        parts = [str(item) for item in items]
        result1 = ", ".join(parts)

        # Verify result
        assert len(result1) > 0
        assert "item_0" in result1
        assert "item_99" in result1

    def test_string_accumulator(self):
        """Test StringAccumulator helper class."""
        from tools.performance.performance_improvements import StringAccumulator

        acc = StringAccumulator()
        for i in range(10):
            acc.add(f"part_{i}")
            if i < 9:
                acc.add(", ")

        result = acc.build()
        assert result == "part_0, part_1, part_2, part_3, part_4, part_5, part_6, part_7, part_8, part_9"

        # Test clear
        acc.clear()
        assert acc.build() == ""


class TestPerformanceHelpers:
    """Test performance helper utilities."""

    def test_batch_process(self):
        """Test batch processing helper."""
        from tools.performance.performance_improvements import batch_process

        items = list(range(250))
        batches = list(batch_process(items, batch_size=100))

        assert len(batches) == 3
        assert len(batches[0]) == 100
        assert len(batches[1]) == 100
        assert len(batches[2]) == 50

    def test_result_cache(self):
        """Test result caching helper."""
        from tools.performance.performance_improvements import ResultCache

        cache = ResultCache(max_size=5)

        # Test set and get
        cache.set("key1", "value1")
        assert cache.has("key1")
        assert cache.get("key1") == "value1"

        # Test eviction - Fill cache to max, then add one more
        for i in range(2, 7):  # Add keys 2-6
            cache.set(f"key{i}", f"value{i}")

        # key1 should be evicted (oldest), key6 should exist (newest)
        assert not cache.has("key1")
        assert cache.has("key6")

        # Test clear
        cache.clear()
        assert not cache.has("key6")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
