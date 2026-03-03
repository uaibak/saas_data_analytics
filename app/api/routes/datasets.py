from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.dataset import DatasetListItem, DatasetPreviewResponse, DatasetUploadResponse
from app.services.dataset_service import (
    build_dataset_preview,
    create_dataset_from_upload,
    get_dataset_for_org,
    list_datasets_for_org,
    soft_delete_dataset,
)

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    name: str = Form(...),
    description: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESEARCHER)),
):
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": "File is required"})
    cleaned_name = name.strip()
    if not cleaned_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": "Dataset name is required"})

    dataset = await create_dataset_from_upload(db, current_user, name=cleaned_name, description=description, file=file)
    columns = sorted(dataset.columns, key=lambda c: c.created_at)
    return DatasetUploadResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        file_size=dataset.file_size,
        row_count=dataset.row_count,
        column_count=dataset.column_count,
        organization_id=dataset.organization_id,
        uploaded_by=dataset.uploaded_by,
        created_at=dataset.created_at,
        columns=columns,
    )


@router.get("", response_model=list[DatasetListItem])
def list_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DatasetListItem]:
    datasets = list_datasets_for_org(db, current_user.organization_id)
    response: list[DatasetListItem] = []
    for dataset in datasets:
        response.append(
            DatasetListItem(
                id=dataset.id,
                name=dataset.name,
                uploaded_by=dataset.uploaded_by,
                uploaded_by_name=dataset.uploader.full_name,
                file_size=dataset.file_size,
                row_count=dataset.row_count,
                created_at=dataset.created_at,
            )
        )
    return response


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def preview_dataset(
    dataset_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DatasetPreviewResponse:
    dataset = get_dataset_for_org(db, dataset_id, current_user.organization_id, active_only=True)
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Dataset not found"})
    return DatasetPreviewResponse(**build_dataset_preview(dataset, page=page, page_size=page_size))


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> None:
    dataset = get_dataset_for_org(db, dataset_id, current_user.organization_id, active_only=True)
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Dataset not found"})
    soft_delete_dataset(db, dataset)
