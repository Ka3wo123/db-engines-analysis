// Constraints
CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (t:Transaction) REQUIRE t.id IS UNIQUE;

// Sample nodes
CREATE (:User {id: 1, name: 'Alice'});
CREATE (:User {id: 2, name: 'Bob'});

CREATE (:Transaction {id: 101, amount: 100.0, is_fraudulent: false});
CREATE (:Transaction {id: 102, amount: 5000.0, is_fraudulent: true});

// Relationships
MATCH (u:User {id:1}), (t:Transaction {id:101})
CREATE (u)-[:MADE]->(t);

MATCH (u:User {id:2}), (t:Transaction {id:102})
CREATE (u)-[:MADE]->(t);
