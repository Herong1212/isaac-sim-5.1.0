import asyncio

import aiohttp

from . import logger


def to_nvdf_form(data: dict):
    """Convert dict to NVDF-compliant form.

    https://confluence.nvidia.com/display/nvdataflow/NVDataFlow#NVDataFlow-PostingPayload
    """

    def _convert(d):
        result = {}

        for key, value in d.items():
            if key.startswith("ts_"):
                result[key] = value
            elif isinstance(value, dict):
                # note that nvdf docs state this should prefix with 'obj_', but without works also.
                # We choose not to as it matches up with existing fields from kit benchmarking
                result[key] = _convert(value)
            elif isinstance(value, str):
                result["s_" + key] = value
            elif isinstance(value, float):
                result["d_" + key] = value
            elif isinstance(value, int):
                result["l_" + key] = value
            else:
                raise ValueError(f"Type {type(value)} not supported in nvdf")
        return result

    return _convert(data)


async def nvdf_send_batched(docs, nvdf_endpoint, batchsize=0):
    """Send docs to nvdf in batches."""
    DEFAULT_BATCHSIZE = 1000
    batchsize = batchsize or DEFAULT_BATCHSIZE
    tasks = []

    while docs:
        docs_batch, docs = docs[:batchsize], docs[batchsize:]
        tasks.append(nvdf_send_batch(docs_batch, nvdf_endpoint))

    if tasks:
        await asyncio.gather(*tasks)


async def nvdf_send_batch(docs, nvdf_endpoint):
    """Send docs to nvdf in a single batch request.

    Args:
        docs (iterable of dict): Docs to send. Gets converted to nvdf form here.
    """
    docs = [to_nvdf_form(x) for x in docs]
    async with aiohttp.ClientSession() as s:
        logger.info("Sending %d profiler docs to %s...", len(docs), nvdf_endpoint)
        await s.post(nvdf_endpoint, json=docs, raise_for_status=True)
