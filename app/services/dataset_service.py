import logging
from pathlib import Path
from uuid import UUID, uuid4

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.dataset import Dataset
from app.models.dataset_column import DatasetColumn
from app.models.user import User
from app.services.file_storage_service import save_upload_file, validate_extension

logger = logging.getLogger(__name__)


def _read_dataset_file(file_path: str) -> pd.DataFrame:
    suffix = Path(file_path).suffix.lower()
    try:
        if suffix == ".csv":
            return pd.read_csv(file_path)
        if suffix == ".xlsx":
            return pd.read_excel(file_path)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": f"Unable to read file: {exc}"})
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": "Unsupported file type"})


def _detect_column_type(series: pd.Series, row_count: int) -> str:
    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    non_null = series.dropna()
    if not non_null.empty:
        parsed = pd.to_datetime(non_null, errors="coerce")
        if parsed.notna().mean() >= 0.9:
            return "datetime"

    unique_count = int(non_null.nunique(dropna=True))
    unique_ratio = (unique_count / row_count) if row_count > 0 else 0.0

    if unique_ratio <= get_settings().CATEGORICAL_UNIQUE_RATIO_THRESHOLD:
        return "categorical"
    return "text"


def _build_columns_metadata(df: pd.DataFrame) -> list[dict]:
    row_count = int(df.shape[0])
    metadata: list[dict] = []
    for column in df.columns:
        series = df[column]
        metadata.append(
            {
                "name": str(column),
                "data_type": _detect_column_type(series, row_count),
                "has_missing_values": bool(series.isna().any()),
                "unique_values_count": int(series.nunique(dropna=True)),
            }
        )
    return metadata


def _serialize_preview_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            return str(value)
    return value


async def create_dataset_from_upload(
    db: Session,
    current_user: User,
    name: str,
    description: str | None,
    file: UploadFile,
) -> Dataset:
    existing = (
        db.query(Dataset)
        .filter(Dataset.organization_id == current_user.organization_id, Dataset.name == name)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Dataset name already exists in this organization"},
        )

    validate_extension(file.filename or "")
    dataset_id = uuid4()
    absolute_path = ""

    try:
        absolute_path, file_size = await save_upload_file(current_user.organization_id, dataset_id, file)
        dataframe = _read_dataset_file(absolute_path)

        row_count = int(dataframe.shape[0])
        column_count = int(dataframe.shape[1])
        columns_metadata = _build_columns_metadata(dataframe)

        dataset = Dataset(
            id=dataset_id,
            name=name,
            description=description,
            file_path=absolute_path,
            file_size=file_size,
            row_count=row_count,
            column_count=column_count,
            uploaded_by=current_user.id,
            organization_id=current_user.organization_id,
            is_active=True,
        )
        db.add(dataset)
        db.flush()

        for column_meta in columns_metadata:
            db.add(DatasetColumn(dataset_id=dataset.id, **column_meta))

        db.commit()
        db.refresh(dataset)
        logger.info(
            "Dataset uploaded: dataset_id=%s org_id=%s user_id=%s file_size=%s",
            dataset.id,
            current_user.organization_id,
            current_user.id,
            file_size,
        )
        return dataset
    except HTTPException:
        db.rollback()
        if absolute_path:
            path = Path(absolute_path)
            path.unlink(missing_ok=True)
            parent = path.parent
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
        raise
    except Exception as exc:
        db.rollback()
        if absolute_path:
            path = Path(absolute_path)
            path.unlink(missing_ok=True)
            parent = path.parent
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": f"Dataset ingestion failed: {exc}"},
        )


def get_dataset_for_org(db: Session, dataset_id: UUID, organization_id: UUID, active_only: bool = True) -> Dataset | None:
    query = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.organization_id == organization_id)
    if active_only:
        query = query.filter(Dataset.is_active.is_(True))
    return query.first()


def list_datasets_for_org(db: Session, organization_id: UUID) -> list[Dataset]:
    return (
        db.query(Dataset)
        .filter(Dataset.organization_id == organization_id, Dataset.is_active.is_(True))
        .order_by(Dataset.created_at.desc())
        .all()
    )


def build_dataset_preview(dataset: Dataset, page: int = 1, page_size: int = 100) -> dict:
    dataframe = _read_dataset_file(dataset.file_path)
    page = max(page, 1)
    page_size = max(min(page_size, 1000), 1)

    start = (page - 1) * page_size
    end = start + page_size
    preview_df = dataframe.iloc[start:end]

    data_rows = []
    for _, row in preview_df.iterrows():
        row_payload = {}
        for col in dataframe.columns:
            row_payload[str(col)] = _serialize_preview_value(row[col])
        data_rows.append(row_payload)

    data_types = {col.name: col.data_type for col in dataset.columns}
    return {
        "dataset_id": dataset.id,
        "name": dataset.name,
        "page": page,
        "page_size": page_size,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "columns": [str(c) for c in dataframe.columns.tolist()],
        "data_types": data_types,
        "preview_rows": data_rows,
    }


def soft_delete_dataset(db: Session, dataset: Dataset) -> None:
    dataset.is_active = False
    db.add(dataset)
    db.commit()
