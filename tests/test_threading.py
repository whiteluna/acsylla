import acsylla
import asyncio
import pytest
import queue
import threading

pytestmark = pytest.mark.asyncio


async def select(session):
    async for row in session.query("select * from test"):
        dict(row)


async def async_task(name, delay, host, keyspace):
    print(f"Task {name} started")
    cluster = acsylla.create_cluster([host])
    cluster.set_log_level("debug")
    session = await cluster.create_session(keyspace=keyspace)
    for i in range(10):
        print(f"Select from {name}")
        await select(session)
        await asyncio.sleep(delay)
    print(f"Task {name} completed")
    await session.close()
    await asyncio.sleep(0.1)


def run_asyncio_in_thread(delay, exc_queue, host, keyspace):
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(async_task(f"test-{threading.current_thread()}", delay, host, keyspace))
    except Exception as e:
        exc_queue.put(e)


class TestThreading:
    async def test_create_cluster_in_thread(self, host, keyspace):
        exc_queue = queue.Queue()
        thread = threading.Thread(target=run_asyncio_in_thread, args=(0, exc_queue, host, keyspace))
        thread.start()
        thread2 = threading.Thread(target=run_asyncio_in_thread, args=(0, exc_queue, host, keyspace))
        thread2.start()
        thread.join()
        thread2.join()
        thread.join()
        thread2.join()
        while True:
            try:
                exc = exc_queue.get(block=False)
            except queue.Empty:
                break
            else:
                raise exc
