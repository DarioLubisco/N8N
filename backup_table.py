import pymssql
import datetime

# Create a timestamped backup table name
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup_table = f"Procurement.por_aprobacion_equivalencias_backup_{timestamp}"
source_table = "Procurement.por_aprobacion_equivalencias"

print(f"Target backup table: {backup_table}")

try:
    print("Connecting to DB...")
    conn = pymssql.connect(
        server="10.147.18.192", 
        port="49751", 
        user="sa", 
        password="Twinc3pt.", 
        database="EnterpriseAdmin_AMC",
        login_timeout=30,
        timeout=120
    )
    cursor = conn.cursor()
    
    # Check if table exists (should not, but safety first)
    # Using SELECT INTO to duplicate the table structure and data
    sql = f"SELECT * INTO {backup_table} FROM {source_table}"
    print(f"Executing: {sql}")
    cursor.execute(sql)
    conn.commit()
    
    # Verify count
    cursor.execute(f"SELECT COUNT(*) FROM {source_table}")
    original_count = cursor.fetchone()[0]
    cursor.execute(f"SELECT COUNT(*) FROM {backup_table}")
    backup_count = cursor.fetchone()[0]
    
    print(f"Backup completed successfully!")
    print(f"Original row count: {original_count}")
    print(f"Backup row count: {backup_count}")
    
    conn.close()
except Exception as e:
    print("Error during backup execution:", e)
