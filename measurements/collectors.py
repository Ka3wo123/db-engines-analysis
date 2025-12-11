def _postgres_collect_metrics(cur, query):
    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
    cur.execute(explain_sql)
    raw = cur.fetchall()[0][0]

    execution_time = raw[0].get("Execution Time")

    return {
        "db_raw": execution_time
    }


def _mysql_collect_metrics(cur, query):
    cur.execute(f"EXPLAIN ANALYZE {query}")
    raw = cur.fetchall()

    return {
        "db_raw": raw
    }


def _cassandra_collect_metrics(session, query: str):
    stmt = session.prepare(query)
    result = session.execute(stmt, trace=True)
    trace = result.get_query_trace()

    return {
        "db_raw": str(trace)
    }


def _neo4j_collect_metrics(driver_connection, query):
    with driver_connection.session() as session:
            result = session.run(query)
            list(result) 
            summary_object = result.consume()
            server_time_ms = summary_object.result_available_after + summary_object.result_consumed_after
            
    return {
        "db_raw": server_time_ms
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
