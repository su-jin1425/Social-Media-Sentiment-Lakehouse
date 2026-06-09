import logging
from typing import Optional, Any

from pyspark.sql import SparkSession, DataFrame

from app.spark.session import create_spark_session

logger = logging.getLogger(__name__)


class DeltaLakeManager:
    """Manages Delta Lake table operations including reads, writes, and maintenance."""

    def __init__(self, spark: Optional[SparkSession] = None, base_path: str = "/data/delta") -> None:
        self._spark = spark or create_spark_session()
        self._base_path = base_path

    def read_table(self, layer: str) -> DataFrame:
        """Read a Delta table from the specified layer (bronze, silver, gold)."""
        path = f"{self._base_path}/{layer}"
        logger.info("Reading Delta table from: %s", path)
        return self._spark.read.format("delta").load(path)

    def read_table_version(self, layer: str, version: int) -> DataFrame:
        """Read a specific version of a Delta table (time travel)."""
        path = f"{self._base_path}/{layer}"
        logger.info("Reading Delta table version %d from: %s", version, path)
        return (
            self._spark.read.format("delta")
            .option("versionAsOf", version)
            .load(path)
        )

    def read_table_as_of(self, layer: str, timestamp: str) -> DataFrame:
        """Read a Delta table as of a specific timestamp."""
        path = f"{self._base_path}/{layer}"
        logger.info("Reading Delta table as of %s from: %s", timestamp, path)
        return (
            self._spark.read.format("delta")
            .option("timestampAsOf", timestamp)
            .load(path)
        )

    def compact_table(self, layer: str) -> None:
        """Run OPTIMIZE (compaction) on a Delta table."""
        path = f"{self._base_path}/{layer}"
        logger.info("Compacting Delta table at: %s", path)
        from delta.tables import DeltaTable
        delta_table = DeltaTable.forPath(self._spark, path)
        delta_table.optimize().executeCompaction()
        logger.info("Compaction complete for: %s", path)

    def vacuum_table(self, layer: str, retention_hours: int = 168) -> None:
        """Remove old files from a Delta table beyond the retention period."""
        path = f"{self._base_path}/{layer}"
        logger.info("Vacuuming Delta table at: %s (retention=%dh)", path, retention_hours)
        from delta.tables import DeltaTable
        delta_table = DeltaTable.forPath(self._spark, path)
        delta_table.vacuum(retention_hours)
        logger.info("Vacuum complete for: %s", path)

    def get_table_history(self, layer: str, limit: int = 20) -> DataFrame:
        """Return the commit history for a Delta table."""
        path = f"{self._base_path}/{layer}"
        from delta.tables import DeltaTable
        delta_table = DeltaTable.forPath(self._spark, path)
        return delta_table.history(limit)

    def get_table_details(self, layer: str) -> dict[str, Any]:
        """Return metadata details about a Delta table."""
        path = f"{self._base_path}/{layer}"
        from delta.tables import DeltaTable
        delta_table = DeltaTable.forPath(self._spark, path)
        detail_df = delta_table.detail()
        row = detail_df.collect()[0]
        return {
            "format": row["format"],
            "id": row["id"],
            "name": row["name"],
            "num_files": row["numFiles"],
            "size_in_bytes": row["sizeInBytes"],
            "created_at": str(row["createdAt"]),
            "last_modified": str(row["lastModified"]),
        }
