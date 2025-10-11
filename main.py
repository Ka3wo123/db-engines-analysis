import glob
import os
import subprocess


def run_cassandra_cql():
    for cql_file in glob.glob("cql/*.cql"):
        filename = os.path.basename(cql_file)
        container_path = f"/cql-init/{filename}"
        subprocess.run([
            "docker", "exec", "-i", "cassandra4",
            "cqlsh",
            "-u", "cassandra",
            "-p", "cassandra",
            "-f", container_path
        ], check=True)
        print(f"Executed {cql_file}")


def run_neo4j_cypher():
    for cypher_file in sorted(glob.glob("cypher/*.cypher")):
        filename = os.path.basename(cypher_file)
        container_path = f"/cypher-init/{filename}"
        subprocess.run([
            "docker", "exec", "-i", "neo4j5",
            "cypher-shell",
            "-u", "neo4j",
            "-p", "cg8&fhjs10LOz",
            "-f", container_path
        ], check=True)
        print(f"✅ Executed {cypher_file}")


if __name__ == "__main__":
    run_cassandra_cql()
    run_neo4j_cypher()
