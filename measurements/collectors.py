import re


def _postgres_collect_metrics(cur, query):
    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
    cur.execute(explain_sql)
    raw = cur.fetchall()[0][0]

    execution_time = raw[0].get("Execution Time")

    return {
        "execution_time_ms": execution_time
    }


def _mysql_collect_metrics(cur, query):
    cur.execute(f"EXPLAIN ANALYZE {query}")
    rows = cur.fetchall()

    execution_time_ms = None
    pattern = re.compile(r"actual time=\d+\.\d+\.\.(\d+\.\d+)")

    for row in rows:
        match = pattern.search(row[0])
        if match:
            execution_time_ms = float(match.group(1))

    return {
        "execution_time_ms": execution_time_ms
    }


def _cassandra_collect_metrics(session, query: str):
    stmt = session.prepare(query)
    result = session.execute(stmt, trace=True)
    trace = result.get_query_trace()

    execution_time_us = trace.duration
    execution_time_ms = execution_time_us.total_seconds() * 1_000.0

    return {
        "execution_time_ms": execution_time_ms
    }


def _neo4j_collect_metrics(driver_connection, query):
    with driver_connection.session() as session:
        result = session.run(query)
        list(result)
        summary_object = result.consume()
        server_time_ms = summary_object.result_available_after + summary_object.result_consumed_after

    return {
        "execution_time_ms": server_time_ms
    }


def run_metrics(db_name: str, connection, query: str):
    match db_name:
        case 'postgresql':
            return _postgres_collect_metrics(connection, query)
        case 'mysql':
            return _mysql_collect_metrics(connection, query)
        case 'neo4j':
            return _neo4j_collect_metrics(connection, query)
        case 'cassandra':
            return _cassandra_collect_metrics(connection, query)
        case _:
            raise Exception('No metrics collector for provided database')
