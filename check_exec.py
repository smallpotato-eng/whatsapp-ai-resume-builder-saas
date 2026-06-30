import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('${N8N_HOME}/database.sqlite')

def resolve(obj, data):
    if isinstance(obj, str):
        try: return resolve(data[int(obj)], data)
        except: return obj
    if isinstance(obj, dict): return {k: resolve(v, data) for k,v in obj.items()}
    if isinstance(obj, list): return [resolve(i, data) for i in obj]
    return obj

row = conn.execute('''
    SELECT ee.id, ee.status, ed.data
    FROM execution_entity ee
    JOIN execution_data ed ON ee.id = ed.executionId
    ORDER BY ee.id DESC LIMIT 1
''').fetchone()

eid, status, raw = row
data = json.loads(raw)
err = resolve(data[5], data)
last = resolve(data[7], data)
run_data = resolve(data[6], data)

print(f'Execution {eid} | status={status} | lastNode={last}')
if isinstance(err, dict) and err.get('message'):
    print(f'ERROR: {err.get("message")}')
    print(f'DESC:  {str(err.get("description",""))[:400]}')
print()
print('Nodes ran:', list(run_data.keys()) if isinstance(run_data, dict) else 'N/A')
conn.close()
