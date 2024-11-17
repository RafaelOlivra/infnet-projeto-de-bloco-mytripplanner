import csv
import json
from typing import Any, Dict
from io import StringIO


class JSONtoCSV:
    @staticmethod
    def _flatten_json(
        data: Dict[str, Any], parent_key: str = "", sep: str = "."
    ) -> Dict[str, Any]:
        """Flatten nested JSON into a flat dictionary."""
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(JSONtoCSV._flatten_json(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Handle lists by creating indexed keys (e.g., list.0.key)
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(
                            JSONtoCSV._flatten_json(
                                item, f"{new_key}{sep}{i}", sep=sep
                            ).items()
                        )
                    else:
                        items.append((f"{new_key}{sep}{i}", item))
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def _unflatten_json(flat_data: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
        """Rebuild nested JSON from a flat dictionary while preserving arrays."""
        unflattened = {}
        for flat_key, value in flat_data.items():
            keys = flat_key.split(sep)
            d = unflattened
            for i, key in enumerate(keys):
                if key.isdigit():  # Handle numeric keys as array indices
                    key = int(key)
                    if not isinstance(d, list):
                        d = [] if not d else [d] if not isinstance(d, list) else d
                    while len(d) <= key:
                        d.append({})
                    if i == len(keys) - 1:
                        d[key] = value
                    else:
                        if not isinstance(d[key], (dict, list)):
                            d[key] = {}
                        d = d[key]
                else:  # Handle string keys as dictionary keys
                    if i == len(keys) - 1:
                        d[key] = value
                    else:
                        d = d.setdefault(key, {})
        return unflattened

    @staticmethod
    def json_to_csv(json_data: Dict[str, Any]) -> str:
        """Convert JSON to CSV and return as a string."""
        flattened_data = JSONtoCSV._flatten_json(json_data)
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=flattened_data.keys())
        writer.writeheader()
        writer.writerow(flattened_data)
        return output.getvalue()

    @staticmethod
    def csv_to_json(csv_string: str) -> Dict[str, Any]:
        """Convert CSV string back to JSON."""
        input_stream = StringIO(csv_string)
        reader = csv.DictReader(input_stream)
        for row in reader:  # Assuming single-row CSV
            return JSONtoCSV._unflatten_json(row)
