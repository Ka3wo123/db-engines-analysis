def _postgres_collect_metrics(cur, query, operation):
    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
    cur.execute(explain_sql)
    raw = cur.fetchall()[0][0]

    execution_time = raw[0].get("Execution Time")

    return {
        "db_name": "postgresql",
        "operation": operation,
        "execution_time_ms": execution_time
    }


def _mysql_collect_metrics(cur, query, operation):
    cur.execute(f"EXPLAIN ANALYZE {query}")
    raw = cur.fetchall()

    return {
        "db_name": "mysql",
        "operation": operation,
        "db_raw": raw
    }


def _cassandra_collect_metrics(session, query: str, operation):
    stmt = session.prepare(query)
    result = session.execute(stmt, trace=True)
    trace = result.get_query_trace()

    return {
        "db_name": "cassandra",
        "operation": operation,
        "db_raw": str(trace)
    }


def _neo4j_collect_metrics(driver_connection, query, operation):
    with driver_connection.session() as session:
        profile_result = session.run(f"PROFILE {query}")
        list(profile_result)
        summary = profile_result.consume().profile

    return {
        "db_name": "neo4j",
        "operation": operation,
        "db_raw": summary
    }


def run_metrics(db_name: str, connection, query: str, operation: str):
    match db_name:
        case 'postgresql':
            return _postgres_collect_metrics(connection, query, operation)
        case 'mysql':
            return _mysql_collect_metrics(connection, query, operation)
        case 'neo4j':
            return _neo4j_collect_metrics(connection, query, operation)
        case 'cassandra':
            return _cassandra_collect_metrics(connection, query, operation)
        case _:
            raise Exception('No metrics collector for provided database')
