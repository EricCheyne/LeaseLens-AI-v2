import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from minio import Minio
from minio.error import S3Error
from ..database import get_db
from ..models import Lease
from ..schemas import Lease as LeaseSchema, LeaseUploadResponse
from ..dependencies import get_current_user, get_current_tenant_id
from ..models import User

router = APIRouter(prefix="/leases", tags=["leases"])

# MinIO client
minio_client = Minio(
    os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    secure=False
)

BUCKET_NAME = os.getenv("MINIO_BUCKET", "leaselens-documents")

def ensure_bucket_exists():
    try:
        if not minio_client.bucket_exists(BUCKET_NAME):
            minio_client.make_bucket(BUCKET_NAME)
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO error: {str(e)}")

@router.post("/upload", response_model=LeaseUploadResponse)
async def upload_lease(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed_types = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF, Word, and text documents are allowed")
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    
    # Ensure bucket exists
    ensure_bucket_exists()
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    tenant_prefix = f"tenant_{tenant_id}/"
    file_path = f"{tenant_prefix}{unique_filename}"
    
    try:
        # Upload to MinIO
        from io import BytesIO
        file_stream = BytesIO(file_content)
        minio_client.put_object(
            BUCKET_NAME,
            file_path,
            file_stream,
            length=len(file_content),
            content_type=file.content_type
        )
        
        # Save to database
        db_lease = Lease(
            tenant_id=tenant_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(file_content),
            content_type=file.content_type,
            uploaded_by=current_user.id,
            status="uploaded"
        )
        db.add(db_lease)
        db.commit()
        db.refresh(db_lease)
        
        return LeaseUploadResponse(
            lease=LeaseSchema.from_orm(db_lease),
            message="Lease document uploaded successfully"
        )
        
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/", response_model=list[LeaseSchema])
def list_leases(
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    leases = db.query(Lease).filter(Lease.tenant_id == tenant_id).all()
    return [LeaseSchema.from_orm(lease) for lease in leases]

@router.get("/{lease_id}", response_model=LeaseSchema)
def get_lease(
    lease_id: int,
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    lease = db.query(Lease).filter(
        Lease.id == lease_id,
        Lease.tenant_id == tenant_id
    ).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    return LeaseSchema.from_orm(lease)