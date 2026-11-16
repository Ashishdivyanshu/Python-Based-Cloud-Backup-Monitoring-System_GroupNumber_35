CLOUD-BASED BACKUP MONITORING SYSTEM Milestone 5 – Project Description
and Run Instructions

1.  PROJECT OVERVIEW This project is a Python-based backup monitoring
    system. It checks whether configured backup files are available,
    whether they are within the permitted backup-age limit, and whether
    their contents remain consistent with the integrity baseline. It
    records monitoring activity and audit events so that changes to
    backup files can be reviewed.

The supplied monitoring output uses a simulated cloud backup storage
location. It demonstrates the monitoring and validation workflow without
requiring a connection to a real cloud provider.

2.  PROJECT FEATURES

-   Backup availability monitoring.
-   Backup freshness checking against a maximum permitted age of 24
    hours.
-   File-integrity verification using hash values and an integrity
    baseline.
-   Monitoring results saved in JSON format.
-   Logging of monitoring activity, warnings, and overall status.
-   Audit trail recording file modification events, including the
    username, action, filename, previous hash, current hash, and
    operation status.

3.  PROJECT FILES AND OUTPUTS Keep the complete project folder structure
    intact when submitting. The main application entry point is app.py.

The following output/support files are included: - backup_monitor.log –
application log containing monitoring events, integrity results,
warnings, and the overall monitoring status. -
backup_monitoring_records.json – structured monitoring output, including
timestamp, storage location, backup availability, freshness, integrity
results, alerts, and overall status. - backup_audit_trail.json – audit
record of file modification activity, including the previous and current
hash values.

The project also uses backup files and any configuration, templates,
static assets, or Python modules present in the original project folder.
Do not remove these files.

4.  REQUIREMENTS

-   Python 3 installed on the computer.
-   pip, Python’s package installer.
-   Flask and any other Python packages imported by the project.

If the project contains a requirements.txt file, install all listed
dependencies using the command in Step 2 below. If there is no
requirements.txt file, install Flask and then install any other missing
packages reported by Python.

5.  HOW TO RUN THE PROJECT

Step 1 – Open the project Extract the submitted project folder, if it is
compressed. Open the folder containing app.py in Visual Studio Code.

Step 2 – Open the VS Code terminal and install dependencies In Visual
Studio Code, select Terminal > New Terminal. Run:

    python -m pip install -r requirements.txt

If requirements.txt is not present, run:

    python -m pip install flask

If Python is not recognized, check that Python is installed and added to
PATH. On some Windows systems, use “py” instead of “python”.

Step 3 – Start the application In the terminal, make sure the current
directory is the folder containing app.py. Run:

    python app.py

Step 4 – Open the application Read the terminal output for the local
address and port printed by Flask. Open that address in a web browser.
Keep the terminal running while using the application.

Step 5 – Perform the demonstration Use the controls and workflow
provided by the application to run backup monitoring and view the
results. The exact buttons, routes, and demonstration sequence depend on
the supplied application code. Do not modify or delete the original
backup files before the initial monitoring run if you want to reproduce
the initial healthy result.

6.  SAMPLE RESULT / VERIFICATION The supplied sample log and JSON
    records show the following demonstration:

-   An integrity baseline was created for three backup files:
    backup_database.txt, backup_documents.txt, and backup_config.txt.
-   During the initial monitoring run, all three backups were reported
    as available, fresh, and integrity-verified. The overall status was
    HEALTHY.
-   A later audit event recorded a successful MODIFY action on
    backup_database.txt by the admin user.
-   During the subsequent monitoring run, all three backups were still
    available and fresh, but backup_database.txt failed the integrity
    check. The other two files passed.
-   The monitoring record therefore reported an INTEGRITY_VIOLATION
    alert for backup_database.txt and an overall status of WARNING.

This demonstrates that a file can remain available and fresh while still
failing an integrity check if its contents have changed.

7.  TROUBLESHOOTING

-   “ModuleNotFoundError: No module named ‘flask’”: Run: python -m pip
    install flask
-   “ModuleNotFoundError” for another package: Install the package named
    in the error using: python -m pip install package_name
-   Flask starts but the page does not open: Use the exact local URL
    printed in the terminal and ensure the application is still running.
-   “requirements.txt” not found: Use the individual installation
    command above, or check whether the project folder includes a
    dependency file under another name.
-   Wrong Python environment: In VS Code, press Ctrl+Shift+P, select
    “Python: Select Interpreter”, and choose the interpreter where the
    project dependencies were installed.

8.  SUBMISSION CHECKLIST Before uploading, ensure the GroupNumber_n
    folder contains:

-   The complete project source code, including app.py and all Python
    modules.
-   All required backup/sample data files.
-   Any templates, static files, configuration files, and dependency
    file used by the application.
-   The generated monitoring and audit output files, if required for the
    demonstration.
-   This descriptive instruction file.

Do not submit only app.py or only the output JSON/log files. Include the
complete project folder so that the evaluator can run the application.

NOTE These instructions are based on the supplied monitoring log and
JSON output files, and on the app.py Flask import shown during setup.
The exact application URL, interface controls, and any additional
dependencies should be confirmed from the final project source code and
requirements file.
