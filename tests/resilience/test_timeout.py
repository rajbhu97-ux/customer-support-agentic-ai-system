import asyncio
import pytest
import logging

from backend.resilience.config import TimeOutConfig
from backend.resilience.timeout import TimeOutManager
from backend.resilience.exceptions import DependencyTimeoutError


@pytest.mark.asyncio
async def test_operation_success():
    config = TimeOutConfig(timeout=3.0)

    async def operation():
        logging.info("Enter inside the function")
        await asyncio.sleep(1)
        return "SUCCESS"

    manager = TimeOutManager(config=config)
    result = await manager.execute(operation)
    assert result == "SUCCESS"


@pytest.mark.asyncio
async def test_config_timeout_operation():
    config = TimeOutConfig(timeout=-2)

    async def operation():
        await asyncio.sleep(1)
        return "SUCCESS"

    with pytest.raises(
        ValueError, match="Timeout must be greater than zero. currently -2"
    ):
        TimeOutManager(config=config)


@pytest.mark.asyncio
async def test_custom_timeout_operation():
    config = TimeOutConfig(timeout=3.0)

    async def operation():
        await asyncio.sleep(1)
        return "SUCCESS"

    manager = TimeOutManager(config=config)

    with pytest.raises(ValueError, match="Timeout should greater than 0. currently -1"):
        await manager.execute(operation, -1)


@pytest.mark.asyncio
async def test_dependancy_timeout_operation():
    config = TimeOutConfig(timeout=3.0)

    async def operation():
        await asyncio.sleep(4.0)
        return "SUCCESS"

    manager = TimeOutManager(config=config)

    with pytest.raises(
        DependencyTimeoutError, match="Dependency call exceeded 3.0 sec"
    ):
        await manager.execute(operation)
