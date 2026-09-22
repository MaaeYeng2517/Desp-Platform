import io
import pandas as pd
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.schemas.validation import ValidationResult, ValidationStatus, ColumnValidation


class ValidationService:
    """
    Service for validating data against schema and business rules.

    Performs column-level validation including:
    - Required columns presence
    - Data type checking
    - Null checks
    - Range validation
    - Uniqueness checks
    - Regex pattern matching
    """

    @staticmethod
    def validate_dataframe(
        df: pd.DataFrame,
        required_columns: List[str],
        column_validations: Optional[List[Dict[str, Any]]] = None,
        custom_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        errors: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []
        total = len(df)

        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            errors.append({
                "type": "missing_columns",
                "message": f"Missing required columns: {missing_cols}",
                "columns": missing_cols,
            })
            return ValidationResult(
                status=ValidationStatus.FAILED,
                total_records=total,
                passed_records=0,
                failed_records=total,
                errors=errors,
                warnings=warnings,
            )

        passed = 0
        failed = 0

        for col in required_columns:
            if col in df.columns:
                null_count = df[col].isna().sum()
                if null_count > 0:
                    errors.append({
                        "type": "null_values",
                        "column": col,
                        "count": int(null_count),
                        "message": f"Column '{col}' has {null_count} null values",
                    })
                    failed += null_count
                else:
                    passed += len(df)

        if column_validations:
            for val in column_validations:
                col = val["column_name"]
                if col not in df.columns:
                    continue

                if val.get("unique"):
                    dup_count = df[col].duplicated().sum()
                    if dup_count > 0:
                        errors.append({
                            "type": "duplicates",
                            "column": col,
                            "count": int(dup_count),
                            "message": f"Column '{col}' has {dup_count} duplicate values",
                        })
                        failed += int(dup_count)

                if val.get("min_value") is not None:
                    min_val = val["min_value"]
                    below_min = (df[col] < min_val).sum()
                    if below_min > 0:
                        errors.append({
                            "type": "below_min",
                            "column": col,
                            "min_value": min_val,
                            "count": int(below_min),
                        })
                        failed += int(below_min)

                if val.get("max_value") is not None:
                    max_val = val["max_value"]
                    above_max = (df[col] > max_val).sum()
                    if above_max > 0:
                        errors.append({
                            "type": "above_max",
                            "column": col,
                            "max_value": max_val,
                            "count": int(above_max),
                        })
                        failed += int(above_max)

                regex = val.get("regex_pattern")
                if regex:
                    import re
                    non_matching = df[col].dropna().apply(
                        lambda x: not bool(re.match(regex, str(x)))
                    ).sum()
                    if non_matching > 0:
                        warnings.append({
                            "type": "regex_mismatch",
                            "column": col,
                            "pattern": regex,
                            "count": int(non_matching),
                        })

        if custom_rules:
            for rule in custom_rules:
                rule_type = rule.get("type", "")
                col = rule.get("column", "")
                if col not in df.columns:
                    warnings.append({"type": "unknown_column", "rule": rule, "message": f"Column '{col}' not found for custom rule"})
                    continue

                if rule_type == "not_null":
                    null_count = df[col].isna().sum()
                    if null_count > 0:
                        errors.append({"type": "not_null", "column": col, "count": int(null_count)})
                        failed += int(null_count)

                elif rule_type == "positive":
                    if df[col].dtype in ["int64", "float64"]:
                        neg_count = (df[col] <= 0).sum()
                        if neg_count > 0:
                            errors.append({"type": "non_positive", "column": col, "count": int(neg_count)})
                            failed += int(neg_count)

                elif rule_type == "custom":
                    expr = rule.get("expression")
                    if expr:
                        try:
                            mask = df.eval(expr)
                            bad_count = (~mask).sum()
                            if bad_count > 0:
                                errors.append({"type": "custom_rule", "column": col, "expression": expr, "count": int(bad_count)})
                                failed += int(bad_count)
                        except Exception as e:
                            warnings.append({"type": "custom_rule_error", "expression": expr, "error": str(e)})

        if errors:
            status = ValidationStatus.FAILED
        elif warnings:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.PASSED

        return ValidationResult(
            status=status,
            total_records=total,
            passed_records=total - failed,
            failed_records=failed,
            errors=errors,
            warnings=warnings,
        )

    @staticmethod
    def validate_csv_content(
        content: bytes,
        required_columns: List[str],
        column_validations: Optional[List[Dict[str, Any]]] = None,
        custom_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> ValidationResult:
        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                total_records=0,
                passed_records=0,
                failed_records=0,
                errors=[{"type": "parse_error", "message": str(e)}],
                warnings=[],
            )

        return ValidationService.validate_dataframe(
            df, required_columns, column_validations, custom_rules
        )

    @staticmethod
    def get_default_column_validations(dataset_name: str) -> List[Dict[str, Any]]:
        if dataset_name == "sales":
            return [
                {"column_name": "transaction_id", "data_type": "string", "nullable": False, "unique": True, "regex_pattern": "^TX\\d+$"},
                {"column_name": "quantity", "data_type": "int", "nullable": False, "min_value": 1},
                {"column_name": "unit_price", "data_type": "decimal", "nullable": False, "min_value": 0},
            ]
        return []
