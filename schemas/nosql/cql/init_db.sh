#!/bin/sh
set -e

docker-entrypoint.sh cassandra &
CASSANDRA_PID=$!

echo "Waiting for Cassandra build up..."
until cqlsh cassandra -e 'DESCRIBE KEYSPACES'; do
    sleep 5
done

KEYSPACE=${CASSANDRA_KEYSPACE:-default_keyspace}

sed "s|{{KEYSPACE}}|${KEYSPACE}|g" /cql-init/create_tables.cql.template > /schema.cql

echo "Applying schema for keyspace: $KEYSPACE"
cqlsh cassandra -f /schema.cql

wait $CASSANDRA_PID