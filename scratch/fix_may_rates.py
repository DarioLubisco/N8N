import pymssql

# Connection configuration
server = '100.94.5.108'
port = '49751'
user = 'sa'
password = 'Twinc3pt.'
database = 'EnterpriseAdmin_AMC'

# Rates to fix
# format: (date_str, bcv_rate, parallel_rate, source)
rates_to_fix = [
    ('2026-05-06', 493.3765, 647.8241, 'api'),
    ('2026-05-07', 496.8301, 649.1067, 'api'),
    ('2026-05-09', 500.4606, 655.6987, 'api'),
    ('2026-05-10', 500.4606, 661.0082, 'api'),
    ('2026-05-11', 500.4606, 666.3176, 'api'),
    ('2026-05-12', 504.9146, 671.6271, 'api'),
    ('2026-05-13', 508.6004, 676.9365, 'api'),
    ('2026-05-14', 510.7873, 682.2460, 'api'),
    ('2026-05-15', 515.1800, 687.5554, 'api'),
    ('2026-05-16', 517.9619, 692.8649, 'api'),
    ('2026-05-17', 517.9619, 698.1743, 'api'),
    ('2026-05-18', 517.9619, 703.4838, 'api'),
    ('2026-05-19', 517.9619, 708.7932, 'api'),
    ('2026-05-20', 520.9142, 714.1027, 'api'),
    ('2026-05-21', 523.6750, 719.4121, 'api'),
    ('2026-05-22', 526.8694, 724.7216, 'api'),
    ('2026-05-23', 530.5047, 730.0310, 'api'),
    ('2026-05-24', 530.5047, 735.3405, 'api'),
]

conn = pymssql.connect(server=server, port=port, user=user, password=password, database=database)
conn.autocommit(True)
cursor = conn.cursor()

try:
    print("Disabling dolartoday trigger...")
    cursor.execute("DISABLE TRIGGER tr_DolarBCV_UpdateSATARJ ON dolartoday")
    
    for date_str, bcv, par, src in rates_to_fix:
        difcamb = round(par / bcv, 6) if bcv > 0 else 0.0
        
        # Check if record exists
        cursor.execute("SELECT id FROM dolartoday WHERE CAST(fecha AS DATE) = %s", (date_str,))
        row = cursor.fetchone()
        
        if row:
            row_id = row[0]
            print(f"Updating date {date_str} (ID: {row_id}) -> BCV: {bcv}, PAR: {par}, DifCamb: {difcamb}")
            cursor.execute("""
                UPDATE dolartoday 
                SET dolarbcv = %s, Dolartoday = %s, DifCamb = %s, fuente = %s
                WHERE id = %s
            """, (bcv, par, difcamb, src, row_id))
        else:
            print(f"Inserting date {date_str} -> BCV: {bcv}, PAR: {par}, DifCamb: {difcamb}")
            cursor.execute("""
                INSERT INTO dolartoday (fecha, _fecha, _hora, Dolartoday, dolarbcv, pendiente, DifCamb, fuente)
                VALUES (%s, dbo.sfAA_FechaClarion(%s), dbo.sfAA_HoraClarion(GETDATE()), %s, %s, 0, %s, %s)
            """, (date_str, date_str, par, bcv, difcamb, src))
            
    print("Enabling dolartoday trigger...")
    cursor.execute("ENABLE TRIGGER tr_DolarBCV_UpdateSATARJ ON dolartoday")
    print("Success! May exchange rates repaired.")
    
except Exception as e:
    print("Error during repair, attempting to re-enable trigger:", e)
    try:
        cursor.execute("ENABLE TRIGGER tr_DolarBCV_UpdateSATARJ ON dolartoday")
        print("Trigger successfully re-enabled.")
    except Exception as re_err:
        print("Failed to re-enable trigger:", re_err)
finally:
    conn.close()
