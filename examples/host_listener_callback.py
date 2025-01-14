import acsylla
import asyncio


def host_listener_callback(event: acsylla.HostListenerEvent, host: str):
    print("1" * 100)
    if event == acsylla.HostListenerEvent.UP:
        print("Host", host, "is UP")
    else:
        print(event.name, host)


async def host_listener_callback2(event: acsylla.HostListenerEvent, host: str):
    print("2" * 200)
    if event == acsylla.HostListenerEvent.UP:
        print("Host", host, "is UP")
    else:
        print(event.name, host)


async def create_table(keyspace, session):
    await session.query(
        f"""
        CREATE KEYSPACE IF NOT EXISTS {keyspace} WITH REPLICATION = {{ 
            'class': 'SimpleStrategy', 'replication_factor': 1
        }}
        """
    )
    await session.use_keyspace(keyspace)
    await session.query(
        """
        CREATE TABLE IF NOT EXISTS test (
            id int PRIMARY KEY,
            value text
        );
        """
    )
    insert = await session.prepared_query("INSERT INTO test (id, value) VALUES (?, ?)")
    await asyncio.gather(*[insert([i, i]) for i in range(100)])
    select = await session.prepared_query("SELECT * FROM test where id in :id")
    async for row in select([(1, 4, 7, 90)]):
        print(row.as_tuple())


import random


async def main():
    cluster_cassandra = acsylla.create_cluster(["localhost"], host_listener_callback=host_listener_callback)
    cluster_scylla = acsylla.create_cluster(
        ["localhost"],
        port=9043,
        local_port_range_min=random.randint(49152, 49252),
        host_listener_callback=host_listener_callback2,
    )
    cassandra = await cluster_cassandra.create_session()
    scylla = await cluster_scylla.create_session()
    await asyncio.gather(
        create_table("test_cassangra", cassandra),
        create_table("test_scylla", scylla),
    )
    await scylla.close()
    del scylla
    cluster_scylla.destroy()
    del cluster_scylla
    await create_table("test_cassangra", cassandra)
    import gc

    gc.collect()
    await asyncio.sleep(5)
    await create_table("test_cassangra", cassandra)
    gc.collect()
    await asyncio.sleep(5)


asyncio.run(main())
