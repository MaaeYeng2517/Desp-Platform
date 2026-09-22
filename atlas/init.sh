#!/bin/sh
set -eu

BASE_URL="${ATLAS_ENDPOINT%/}"
PAYLOAD='{
  "entities": [
    {
      "typeName": "hive_db",
      "attributes": {
        "qualifiedName": "raw@data-platform",
        "name": "raw",
        "description": "Raw ingestion schema for the Data Engineering Workflow Platform",
        "owner": "dataeng",
        "clusterName": "data-platform"
      },
      "relationshipAttributes": {}
    },
    {
      "typeName": "hive_table",
      "attributes": {
        "qualifiedName": "raw.sales@data-platform",
        "name": "sales",
        "description": "Raw sales transactions loaded from MinIO",
        "owner": "dataeng",
        "comment": "Bronze sales dataset",
        "tableType": "MANAGED_TABLE"
      },
      "relationshipAttributes": {
        "db": {
          "typeName": "hive_db",
          "uniqueAttributes": {
            "qualifiedName": "raw@data-platform"
          }
        }
      }
    },
    {
      "typeName": "hive_column",
      "attributes": {
        "qualifiedName": "raw.sales.transaction_id@data-platform",
        "name": "transaction_id",
        "type": "string",
        "comment": "Unique transaction identifier",
        "position": 0
      },
      "relationshipAttributes": {
        "table": {
          "typeName": "hive_table",
          "uniqueAttributes": {
            "qualifiedName": "raw.sales@data-platform"
          }
        }
      }
    },
    {
      "typeName": "hive_column",
      "attributes": {
        "qualifiedName": "raw.sales.transaction_date@data-platform",
        "name": "transaction_date",
        "type": "date",
        "comment": "Transaction date",
        "position": 1
      },
      "relationshipAttributes": {
        "table": {
          "typeName": "hive_table",
          "uniqueAttributes": {
            "qualifiedName": "raw.sales@data-platform"
          }
        }
      }
    },
    {
      "typeName": "hive_column",
      "attributes": {
        "qualifiedName": "raw.sales.customer_id@data-platform",
        "name": "customer_id",
        "type": "string",
        "comment": "Customer identifier",
        "position": 2
      },
      "relationshipAttributes": {
        "table": {
          "typeName": "hive_table",
          "uniqueAttributes": {
            "qualifiedName": "raw.sales@data-platform"
          }
        }
      }
    }
  ]
}'

until curl -fsS -u "${ATLAS_USERNAME}:${ATLAS_PASSWORD}" "${BASE_URL}/api/atlas/admin/version" >/dev/null; do
  echo "Waiting for Apache Atlas..."
  sleep 5
done

response="$(curl -fsS -u "${ATLAS_USERNAME}:${ATLAS_PASSWORD}" -H 'Content-Type: application/json' -H 'Accept: application/json' -d "${PAYLOAD}" "${BASE_URL}/api/atlas/v2/entity/bulk")"
printf '%s\n' "${response}"
