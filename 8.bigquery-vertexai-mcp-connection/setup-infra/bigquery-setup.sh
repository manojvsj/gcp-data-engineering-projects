#!/bin/bash

# ============================================
# BigQuery Setup Script
# ============================================
# This script creates a BigQuery dataset, table, and populates it with sample data
# It reads configuration from environment variables set in setup.sh
# ============================================

echo "📊 Starting BigQuery setup..."
echo "Project: $PROJECT_ID"
echo "Dataset: $DATASET_ID"
echo "Table: $TABLE_ID"
echo "Location: $REGION"
echo ""

# ============================================
# Create BigQuery Dataset
# ============================================
echo "📁 Creating BigQuery dataset: $DATASET_ID..."

bq --location=$REGION mk \
  --dataset \
  --description="Sales data for MCP demo application" \
  $PROJECT_ID:$DATASET_ID 2>/dev/null || echo "Dataset $DATASET_ID already exists"

# ============================================
# Create BigQuery Table
# ============================================
echo "📋 Creating BigQuery table: $TABLE_ID..."

bq mk \
  --table \
  --description="Orders table with sales data" \
  $PROJECT_ID:$DATASET_ID.$TABLE_ID \
  order_id:STRING,customer_name:STRING,product:STRING,quantity:INTEGER,price:FLOAT,order_date:DATE,region:STRING \
  2>/dev/null || echo "Table $TABLE_ID already exists"

# ============================================
# Locate Sample Data File
# ============================================
echo "📝 Loading sample data..."

# Get the directory where this script is located
SAMPLE_DATA_FILE="sample-data.json"

# Check if sample data file exists
if [ ! -f "$SAMPLE_DATA_FILE" ]; then
    echo "❌ Error: Sample data file not found at $SAMPLE_DATA_FILE"
    exit 1
fi

echo "Using sample data file: $SAMPLE_DATA_FILE"

# ============================================
# Load Sample Data into BigQuery
# ============================================
echo "⬆️  Loading sample data into BigQuery..."

bq load \
  --source_format=NEWLINE_DELIMITED_JSON \
  --replace \
  $PROJECT_ID:$DATASET_ID.$TABLE_ID \
  $SAMPLE_DATA_FILE \
  order_id:STRING,customer_name:STRING,product:STRING,quantity:INTEGER,price:FLOAT,order_date:DATE,region:STRING

# ============================================
# Verify Data Load
# ============================================
echo ""
echo "✅ Verifying data load..."

ROW_COUNT=$(bq query --use_legacy_sql=false --format=csv "SELECT COUNT(*) as count FROM \`$PROJECT_ID.$DATASET_ID.$TABLE_ID\`" | tail -n 1)

echo "Total rows loaded: $ROW_COUNT"


# ============================================
echo ""
echo "✅ BigQuery setup completed successfully!"
echo "=================================="
echo "Dataset: $PROJECT_ID:$DATASET_ID"
echo "Table: $PROJECT_ID:$DATASET_ID.$TABLE_ID"
echo "Rows: $ROW_COUNT"
echo ""
echo "You can now query this data using:"
echo "bq query --use_legacy_sql=false 'SELECT * FROM \`$PROJECT_ID.$DATASET_ID.$TABLE_ID\` LIMIT 10'"
echo "=================================="
