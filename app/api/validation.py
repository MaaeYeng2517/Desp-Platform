from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.services.validation_service import ValidationService
from app.services.cleaning_service import CleaningService
from app.api.deps import get_cleaning_service
from app.schemas.validation import ValidationResult, CleaningRequest

router = APIRouter(
    prefix="/validation",
    tags=["Validation"],
)


@router.post("/check", response_model=ValidationResult)
async def validate_file(
    file: UploadFile = File(...),
    dataset_name: str = "sales",
    custom_rules: Optional[str] = None,
):
    import json

    content = await file.read()
    required_columns = ["transaction_id", "transaction_date", "customer_id", "product_id", "quantity", "unit_price"] if dataset_name == "sales" else []
    column_validations = ValidationService.get_default_column_validations(dataset_name)

    rules = None
    if custom_rules:
        try:
            rules = json.loads(custom_rules)
        except json.JSONDecodeError:
            pass

    return ValidationService.validate_csv_content(
        content,
        required_columns=required_columns,
        column_validations=column_validations,
        custom_rules=rules,
    )


@router.post("/validate-and-clean", response_model=dict)
async def validate_and_clean(
    file: UploadFile = File(...),
    dataset_name: str = "sales",
    cleaning_params: Optional[str] = None,
):
    import json
    import io
    import pandas as pd

    content = await file.read()

    cleaning_request = CleaningRequest()
    if cleaning_params:
        try:
            params = json.loads(cleaning_params)
            cleaning_request = CleaningRequest(**params)
        except (json.JSONDecodeError, Exception):
            pass

    df = pd.read_csv(io.BytesIO(content))

    validation_result = ValidationService.validate_dataframe(
        df,
        required_columns=["transaction_id"] if "transaction_id" in df.columns else [],
        column_validations=ValidationService.get_default_column_validations(dataset_name),
    )

    cleaned_df = CleaningService.clean_dataframe(df, cleaning_request)

    output = io.StringIO()
    cleaned_df.to_csv(output, index=False)
    cleaned_content = output.getvalue()

    return {
        "validation": validation_result.model_dump(),
        "cleaned_rows": len(cleaned_df),
        "original_rows": len(df),
        "cleaned_data": cleaned_content[:5000],
    }


@router.post("/columns", response_model=dict)
async def get_column_info(
    file: UploadFile = File(...),
    dataset_name: str = "sales",
):
    import io
    import pandas as pd

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    columns = []
    for col in df.columns:
        col_info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "null_count": int(df[col].isna().sum()),
            "unique_count": int(df[col].nunique()),
            "sample_values": df[col].dropna().head(5).tolist() if len(df) > 0 else [],
        }
        columns.append(col_info)

    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": columns,
    }
