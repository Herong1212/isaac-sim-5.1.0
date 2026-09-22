# Usage Examples

## Run a Coroutine Using Async Engine

```python
import asyncio
from omni.kit.async_engine import run_coroutine

async def async_multiply(x, y):
    await asyncio.sleep(1)  # Simulate an async operation
    return x * y

# Run the coroutine using the async engine
task = run_coroutine(async_multiply(6, 7))
```
