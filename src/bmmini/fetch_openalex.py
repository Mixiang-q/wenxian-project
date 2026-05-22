import os
import argparse
import json
import yaml
import requests
import time
from typing import Dict, Any


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def build_boolean_queries():

    group1 = [
        "nanowire",
        "nanowires"
    ]

    group2 = [
        "synaptic",
        "neuromorphic",
        "memristor",
        "artificial synapse",
        "synaptic transistor"
    ]

    queries = []

    for t1 in group1:
        for t2 in group2:
            queries.append(f"{t1} {t2}")

    return queries


def fetch_works(config: Dict[str, Any]) -> None:

    base_url = config['data_source']['base_url']

    from_year = config['query']['from_year']
    to_year = config['query']['to_year']

    max_records = config['query'].get('max_records', 5000)

    output_path = os.path.join(
        config['output']['data_dir'].replace('processed', 'raw'),
        'openalex_works.jsonl'
    )

    api_key = os.environ.get('OPENALEX_API_KEY')

    headers = {
        "User-Agent": "mailto:your_email@example.com"
    }

    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'

    queries = build_boolean_queries()

    seen_ids = set()

    records_fetched = 0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:

        for query in queries:

            print(f"\n==========")
            print(f"Query: {query}")
            print(f"==========\n")

            cursor = '*'

            while cursor and records_fetched < max_records:

                params = {

                    'filter': (
                        f'default.search:{query},'
                        f'publication_year:{from_year}-{to_year},'
                        'has_references:true'
                    ),

                    'per_page': 100,

                    'cursor': cursor,

                    'select': ','.join([
                        'id',
                        'display_name',
                        'doi',
                        'publication_year',
                        'cited_by_count',
                        'authorships',
                        'keywords',
                        'topics',
                        'primary_location',
                        'referenced_works'
                    ])
                }

                response = None

                max_retries = 5

                for attempt in range(max_retries):

                    try:

                        response = requests.get(
                            f"{base_url}/works",
                            params=params,
                            headers=headers,
                            timeout=300
                        )

                        response.raise_for_status()

                        break

                    except requests.exceptions.RequestException as e:

                        print(
                            f"Request failed "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )

                        print(e)

                        if response is not None:
                            print(f"Status: {response.status_code}")

                        if attempt < max_retries - 1:

                            print("Retrying in 5 seconds...\n")

                            time.sleep(5)

                        else:

                            print("Skipping this query.\n")

                            response = None

                if response is None:
                    break

                data = response.json()

                results = data.get('results', [])

                if not results:
                    break

                new_count = 0

                for work in results:

                    work_id = work.get('id')

                    if not work_id:
                        continue

                    if work_id in seen_ids:
                        continue

                    seen_ids.add(work_id)

                    json.dump(work, f, ensure_ascii=False)
                    f.write('\n')

                    records_fetched += 1
                    new_count += 1

                    if records_fetched >= max_records:
                        break

                print(
                    f"Fetched: {records_fetched} total "
                    f"(+{new_count} new)"
                )

                cursor = data.get('meta', {}).get('next_cursor')

                time.sleep(1)

    print("\n======================")
    print("Finished.")
    print(f"Total unique records: {records_fetched}")
    print(f"Saved to: {output_path}")
    print("======================\n")


def main():

    parser = argparse.ArgumentParser(
        description='Fetch works from OpenAlex'
    )

    parser.add_argument(
        '--config',
        default='config/query.yaml',
        help='Path to configuration file'
    )

    args = parser.parse_args()

    config = load_config(args.config)

    fetch_works(config)


if __name__ == '__main__':
    main()
