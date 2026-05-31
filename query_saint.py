import pymssql
import sys
import json

def run_query(query):
    server = "10.147.18.192"
    user = "sa"
    password = "Twinc3pt."
    database = "EnterpriseAdmin_AMC"

    try:
        conn = pymssql.connect(server, user, password, database)
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 query_saint.py \"QUERY_SQL\"")
        sys.exit(1)
    
    query = sys.argv[1]
    res = run_query(query)
    print(json.dumps(res, indent=2, default=str))
