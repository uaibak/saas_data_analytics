from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DatasetColumnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dataset_id: UUID
    name: str
    data_type: str
    has_missing_values: bool
    unique_values_count: int
    created_at: datetime


class DatasetUploadResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    file_size: int
    row_count: int
    column_count: int
    organization_id: UUID
    uploaded_by: UUID
    created_at: datetime
    columns: list[DatasetColumnOut]


class DatasetListItem(BaseModel):
    id: UUID
    name: str
    uploaded_by: UUID
    uploaded_by_name: str
    file_size: int
    row_count: int
    created_at: datetime


class DatasetPreviewResponse(BaseModel):
    dataset_id: UUID
    name: str
    page: int
    page_size: int
    row_count: int
    column_count: int
    columns: list[str]
    data_types: dict[str, str]
    preview_rows: list[dict[str, Any]]
