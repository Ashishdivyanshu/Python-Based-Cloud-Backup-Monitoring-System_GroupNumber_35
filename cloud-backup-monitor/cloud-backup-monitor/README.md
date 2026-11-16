# BackupGuard – Cloud Backup Monitoring (CSET 462)

A website around the notebook's Python monitoring system. `app.py` contains the notebook's
functions (availability, freshness, SHA-256, baseline, integrity, audit trail, create/modify/delete,
logging, integrated engine) with their logic unchanged. Flask only exposes them over HTTP.

## Run
    pip install -r requirements.txt
    python app.py
Open http://127.0.0.1:5000

## Files created at runtime (same as the notebook)
simulated_cloud_backup/, backup_monitor.log, backup_audit_trail.json,
backup_monitoring_records.json, backup_integrity_baseline.json

## Pages
Dashboard (run monitoring) · Backups (create / modify / delete) · Integrity baseline · Audit trail · Security log · About
