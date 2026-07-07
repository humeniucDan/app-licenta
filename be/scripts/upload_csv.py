import argparse
import csv
import json
import sys
import uuid
from datetime import datetime

from sqlalchemy import create_engine, insert
from sqlalchemy.orm import Session

sys.path.insert(0, ".")
from model.orm.timestamp import TimeStamp
from model.orm.dataseries import DataSeries


def parse_args():
    parser = argparse.ArgumentParser(description="Upload a CSV to a data series.")
    parser.add_argument("--data-series-id", required=True, type=uuid.UUID, help="UUID of the target data series")
    parser.add_argument("--csv", required=True, help="Path to the CSV file")
    parser.add_argument("--date-column", default="date", help="Name of the date column in the CSV")
    parser.add_argument("--db-url", default="postgresql+psycopg://postgres:postgres@localhost:5433/koop", help="Database URL")
    parser.add_argument("--batch-size", type=int, default=1000, help="Rows per insert batch")
    return parser.parse_args()


def main():
    args = parse_args()

    engine = create_engine(args.db_url)
    with Session(engine) as session:
        exists = session.query(DataSeries).filter(DataSeries.id == args.data_series_id).first()
        if not exists:
            print(f"Error: DataSeries with id '{args.data_series_id}' not found.", file=sys.stderr)
            sys.exit(1)

    with open(args.csv, newline="") as f:
        reader = csv.DictReader(f)
        if args.date_column not in reader.fieldnames:
            print(f"Error: CSV has no '{args.date_column}' column. Columns: {reader.fieldnames}", file=sys.stderr)
            sys.exit(1)

        value_columns = [c for c in reader.fieldnames if c != args.date_column]
        batch = []
        total = 0

        with Session(engine) as session:
            for row in reader:
                try:
                    parsed_date = datetime.fromisoformat(row[args.date_column])
                except ValueError:
                    print(f"Skipping row {total + 1}: invalid date '{row[args.date_column]}'", file=sys.stderr)
                    continue

                value = {col: row[col] for col in value_columns}
                batch.append({
                    "date": parsed_date,
                    "value": value,
                    "data_series_id": args.data_series_id,
                })

                if len(batch) >= args.batch_size:
                    session.execute(insert(TimeStamp), batch)
                    session.commit()
                    total += len(batch)
                    print(f"Inserted {total} rows...")
                    batch = []

            if batch:
                session.execute(insert(TimeStamp), batch)
                session.commit()
                total += len(batch)

    print(f"Done. Inserted {total} timestamps into data series {args.data_series_id}.")


if __name__ == "__main__":
    main()
