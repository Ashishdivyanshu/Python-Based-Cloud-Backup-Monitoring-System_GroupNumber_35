"""Cloud Backup Monitoring System - web app.
Every monitoring function below is the notebook's logic, unchanged.
Flask only exposes it over HTTP."""
import os, json, csv, hashlib, logging
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, jsonify, request

os.chdir(Path(__file__).resolve().parent)

# ---------- Milestone 2: environment ----------
BASE_DIR = Path("simulated_cloud_backup")
BASE_DIR.mkdir(exist_ok=True)

sample_backups = {
    "backup_database.txt": "Sample database backup data",
    "backup_documents.txt": "Sample documents backup data",
    "backup_config.txt": "Sample configuration backup data",
}
for filename, content in sample_backups.items():
    file_path = BASE_DIR / filename
    if not file_path.exists():
        file_path.write_text(content)

MAX_BACKUP_AGE_HOURS = 24
expected_backups = list(sample_backups.keys())

# ---------- Milestone 3: configuration ----------
LOG_FILE = Path("backup_monitor.log")
AUDIT_FILE = Path("backup_audit_trail.json")
RECORDS_FILE = Path("backup_monitoring_records.json")
BASELINE_FILE = Path("backup_integrity_baseline.json")

# ---------- Module 1: security logging ----------
logger = logging.getLogger("BackupMonitoring")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
logger.info("Backup monitoring logging initialized.")


# ---------- Module 2: availability ----------
def check_backup_availability():
    results = {}
    for filename in expected_backups:
        file_path = BASE_DIR / filename
        if file_path.is_file():
            results[filename] = "AVAILABLE"
            logger.info("Backup available: %s", filename)
        else:
            results[filename] = "MISSING"
            logger.warning("Missing backup detected: %s", filename)
    return results


# ---------- Module 3: freshness ----------
def check_backup_freshness():
    results = {}
    current_time = datetime.now()
    maximum_age = timedelta(hours=MAX_BACKUP_AGE_HOURS)
    for filename in expected_backups:
        file_path = BASE_DIR / filename
        if not file_path.is_file():
            results[filename] = {"status": "MISSING", "age_hours": None}
            continue
        modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        backup_age = current_time - modified_time
        age_hours = backup_age.total_seconds() / 3600
        if backup_age.total_seconds() < 0:
            status = "INVALID_FUTURE_TIMESTAMP"
            logger.warning("Future modification timestamp: %s", filename)
        elif backup_age > maximum_age:
            status = "OUTDATED"
            logger.warning("Outdated backup: %s (%.2f hours old)", filename, age_hours)
        else:
            status = "FRESH"
            logger.info("Backup is fresh: %s", filename)
        results[filename] = {"status": status, "age_hours": round(age_hours, 2)}
    return results


# ---------- Module 4: SHA-256 ----------
def calculate_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


# ---------- Module 5: baseline ----------
def create_integrity_baseline():
    baseline = {}
    for filename in expected_backups:
        file_path = BASE_DIR / filename
        if not file_path.is_file():
            logger.warning("Cannot create baseline; backup missing: %s", filename)
            continue
        baseline[filename] = calculate_sha256(file_path)
    with open(BASELINE_FILE, "w", encoding="utf-8") as file:
        json.dump(baseline, file, indent=4)
    logger.info("Integrity baseline created for %d backups.", len(baseline))
    return baseline


# ---------- Module 6: integrity verification ----------
def check_backup_integrity(baseline=None):
    if baseline is None:
        if not BASELINE_FILE.is_file():
            raise FileNotFoundError(
                "Integrity baseline not found. Create the baseline before checking integrity.")
        with open(BASELINE_FILE, "r", encoding="utf-8") as file:
            baseline = json.load(file)
    results = {}
    for filename in expected_backups:
        file_path = BASE_DIR / filename
        if not file_path.is_file():
            results[filename] = "MISSING"
            continue
        if filename not in baseline:
            results[filename] = "NO_BASELINE"
            logger.warning("No integrity baseline exists for: %s", filename)
            continue
        if calculate_sha256(file_path) == baseline[filename]:
            results[filename] = "INTEGRITY_OK"
            logger.info("Integrity verified: %s", filename)
        else:
            results[filename] = "INTEGRITY_VIOLATION"
            logger.warning("Integrity violation detected: %s", filename)
    return results


# ---------- Module 7: audit trail ----------
def record_audit_event(username, action, filename, previous_hash=None,
                       current_hash=None, status="SUCCESS"):
    event = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "username": username, "action": action, "filename": filename,
        "previous_hash": previous_hash, "current_hash": current_hash, "status": status,
    }
    if AUDIT_FILE.exists():
        with open(AUDIT_FILE, "r", encoding="utf-8") as file:
            audit_records = json.load(file)
    else:
        audit_records = []
    audit_records.append(event)
    with open(AUDIT_FILE, "w", encoding="utf-8") as file:
        json.dump(audit_records, file, indent=4)
    logger.info("Audit event: user=%s action=%s file=%s status=%s",
                username, action, filename, status)
    return event


# ---------- Module 8: controlled operations ----------
def modify_backup(filename, new_content, username):
    if Path(filename).name != filename:
        raise ValueError("Invalid backup filename.")
    file_path = BASE_DIR / filename
    if not file_path.is_file():
        record_audit_event(username=username, action="MODIFY", filename=filename,
                           status="FAILED_MISSING")
        raise FileNotFoundError(filename)
    previous_hash = calculate_sha256(file_path)
    try:
        file_path.write_text(new_content, encoding="utf-8")
        current_hash = calculate_sha256(file_path)
        record_audit_event(username=username, action="MODIFY", filename=filename,
                           previous_hash=previous_hash, current_hash=current_hash,
                           status="SUCCESS")
    except Exception:
        logger.exception("Backup modification failed: %s", filename)
        raise


def create_backup(filename, content, username):
    if Path(filename).name != filename:
        raise ValueError("Invalid backup filename.")
    if not filename.endswith(".txt"):
        raise ValueError("Only .txt backup files are allowed.")
    file_path = BASE_DIR / filename
    if file_path.exists():
        raise FileExistsError(filename)
    try:
        with file_path.open("x", encoding="utf-8") as file:
            file.write(content)
        current_hash = calculate_sha256(file_path)
        record_audit_event(username=username, action="CREATE", filename=filename,
                           current_hash=current_hash, status="SUCCESS")
    except Exception:
        logger.exception("Backup creation failed: %s", filename)
        raise


def delete_backup(filename, username):
    if Path(filename).name != filename:
        raise ValueError("Invalid backup filename.")
    if not filename.endswith(".txt"):
        raise ValueError("Only .txt backup files are allowed.")
    file_path = BASE_DIR / filename
    if not file_path.is_file():
        record_audit_event(username=username, action="DELETE", filename=filename,
                           status="FAILED_MISSING")
        raise FileNotFoundError(filename)
    previous_hash = calculate_sha256(file_path)
    try:
        file_path.unlink()
        record_audit_event(username=username, action="DELETE", filename=filename,
                           previous_hash=previous_hash, status="SUCCESS")
    except Exception:
        logger.exception("Backup deletion failed: %s", filename)
        raise


# ---------- Module 9: integrated monitoring engine ----------
def run_backup_monitoring():
    availability = check_backup_availability()
    freshness = check_backup_freshness()
    integrity = check_backup_integrity()
    alerts = []
    for filename in expected_backups:
        if availability[filename] == "MISSING":
            alerts.append({"filename": filename, "issue": "MISSING_BACKUP"})
        freshness_status = freshness[filename]["status"]
        if freshness_status in ("OUTDATED", "INVALID_FUTURE_TIMESTAMP"):
            alerts.append({"filename": filename, "issue": freshness_status})
        integrity_status = integrity[filename]
        if integrity_status in ("INTEGRITY_VIOLATION", "NO_BASELINE"):
            alerts.append({"filename": filename, "issue": integrity_status})
    report = {
        "monitoring_timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "storage_location": str(BASE_DIR),
        "maximum_backup_age_hours": MAX_BACKUP_AGE_HOURS,
        "availability": availability, "freshness": freshness, "integrity": integrity,
        "alerts": alerts, "overall_status": "WARNING" if alerts else "HEALTHY",
    }
    with open(RECORDS_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)
    logger.info("Monitoring completed. Status: %s", report["overall_status"])
    return report


# First launch only: trusted reference hashes (notebook Test 1)
if not BASELINE_FILE.is_file():
    create_integrity_baseline()

# =================== Web layer ===================
app = Flask(__name__, static_folder="static", static_url_path="/static")


def _body():
    d = request.get_json(silent=True) or {}
    return (d.get("username") or "").strip(), d


@app.errorhandler(ValueError)
def _bad(e): return jsonify(error=str(e)), 400
@app.errorhandler(FileExistsError)
def _exists(e): return jsonify(error=f"Backup already exists: {e}"), 409
@app.errorhandler(FileNotFoundError)
def _missing(e): return jsonify(error=f"Not found: {e}"), 404


@app.get("/")
def index(): return app.send_static_file("index.html")


@app.get("/api/config")
def api_config():
    return jsonify(storage=str(BASE_DIR), max_age_hours=MAX_BACKUP_AGE_HOURS,
                   expected=expected_backups)


@app.post("/api/monitor")
def api_monitor(): return jsonify(run_backup_monitoring())


@app.get("/api/backups")
def api_backups():
    out = []
    for p in sorted(BASE_DIR.iterdir()):
        if p.is_file():
            st = p.stat()
            out.append({"filename": p.name, "size": st.st_size,
                        "modified": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                        "sha256": calculate_sha256(p), "monitored": p.name in expected_backups})
    return jsonify(out)


@app.get("/api/backups/<filename>")
def api_backup_get(filename):
    if Path(filename).name != filename:
        raise ValueError("Invalid backup filename.")
    p = BASE_DIR / filename
    if not p.is_file():
        raise FileNotFoundError(filename)
    return jsonify(filename=filename, content=p.read_text(encoding="utf-8"))


@app.post("/api/backups")
def api_backup_create():
    user, d = _body()
    if not user: raise ValueError("Username is required.")
    create_backup(d.get("filename", ""), d.get("content", ""), user)
    return jsonify(ok=True)


@app.put("/api/backups/<filename>")
def api_backup_modify(filename):
    user, d = _body()
    if not user: raise ValueError("Username is required.")
    modify_backup(filename, d.get("content", ""), user)
    return jsonify(ok=True)


@app.delete("/api/backups/<filename>")
def api_backup_delete(filename):
    user, _ = _body()
    if not user: raise ValueError("Username is required.")
    delete_backup(filename, user)
    return jsonify(ok=True)


@app.get("/api/baseline")
def api_baseline():
    return jsonify(json.loads(BASELINE_FILE.read_text(encoding="utf-8")))


@app.post("/api/baseline")
def api_baseline_create(): return jsonify(create_integrity_baseline())


@app.get("/api/audit")
def api_audit():
    if not AUDIT_FILE.exists(): return jsonify([])
    return jsonify(json.loads(AUDIT_FILE.read_text(encoding="utf-8"))[::-1])


@app.get("/api/log")
def api_log():
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines() if LOG_FILE.exists() else []
    return jsonify(lines[-200:][::-1])


@app.get("/api/report")
def api_report():
    if not RECORDS_FILE.exists(): return jsonify(None)
    return jsonify(json.loads(RECORDS_FILE.read_text(encoding="utf-8")))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
