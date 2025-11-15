def _postgres_collect_metrics(cur, query, operation, records=0):
    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
    cur.execute(explain_sql)
    raw = cur.fetchall()[0][0]

    execution_time = raw[0].get("Execution Time")

    return {
        "db_name": "postgresql",
        "operation": operation,
        "execution_time_ms": execution_time
    }


def _mysql_collect_metrics(cur, query, operation, records=0):
    cur.execute(f"EXPLAIN ANALYZE {query}")
    raw = cur.fetchall()

    text = " ".join([str(r[0]) for r in raw])
    execution_time = None

    if "timing=" in text:
        execution_time = float(text.split("timing=")[1].split("ms")[0])

    return {
        "db_name": "mysql",
        "operation": operation,
        "execution_time_ms": execution_time
    }


def _cassandra_collect_metrics(session, query: str, operation, records=0):
    stmt = session.prepare(query)
    result = session.execute(stmt, trace=True)
    trace = result.get_query_trace()

    return {
        "db_name": "cassandra",
        "operation": operation,
        "execution_time_ms": trace.duration
    }


def _neo4j_collect_metrics(driver_connection, query, operation, records=0):
    with driver_connection.session() as session:
        profile_result = session.run(f"EXPLAIN {query}")
        list(profile_result)
        summary = profile_result.consume().profile
        print(summary)



    return {
        "db_name": "neo4j",
        "operation": operation,
        "execution_time_ms": 0
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
