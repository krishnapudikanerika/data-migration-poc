import os
import yaml
import pandas as pd
from datacompy import PandasCompare
import pytest
from sqlalchemy import create_engine


def load_config():
    """Reads migration table definitions from the YAML config file."""
    config_path = os.path.join("config", "migration_config.yaml")
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)["migrations"]


def load_dataset(source_type, path_or_query, connection_string=None):
    """Generic data loader supporting CSVs now and SQL databases later."""
    if source_type == "csv":
        return pd.read_csv(path_or_query)
    elif source_type == "sql":
        engine = create_engine(connection_string)
        return pd.read_sql(path_or_query, engine)
    else:
        raise ValueError(f"Unsupported source_type: {source_type}")


@pytest.mark.parametrize("migration", load_config(), ids=lambda m: m["table_name"])
def test_data_migration(migration):
    """Generic test case executed dynamically for every table in YAML config."""
    table_name = migration["table_name"]

    # 1. Load Source and Target Data
    df_source = load_dataset(
        migration["source_type"],
        migration["source_path"],
        migration.get("source_conn")
    )
    df_target = load_dataset(
        migration["target_type"],
        migration["target_path"],
        migration.get("target_conn")
    )

    # 2. Perform Automated Reconciliation via DataComPy
    comparison = PandasCompare(
        df1=df_source,
        df2=df_target,
        join_columns=migration["join_columns"],
        abs_tol=migration.get("abs_tol", 0),
        df1_name="Legacy_Source",
        df2_name="Migrated_Target"
    )

    # 3. Generate Standalone Text Audit Report
    os.makedirs("reports", exist_ok=True)
    audit_file = os.path.join("reports", f"{table_name}_audit_report.txt")
    with open(audit_file, "w", encoding="utf-8") as report:
        report.write(comparison.report())

    # 4. Assert Zero Mismatches (Fails test & prints full diff in HTML report if mismatched)
    assert comparison.matches(), (
        f"\n[FAILED] Data discrepancy detected in table: '{table_name}'\n"
        f"Full audit saved to: {audit_file}\n\n"
        f"{comparison.report()}"
    )
