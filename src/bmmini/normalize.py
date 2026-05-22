import os
import json
import argparse
import pandas as pd
from typing import Dict, Any, List


def get_nested(data: Any, *keys) -> Any:
    """Safely get nested dictionary values."""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return None
        if result is None:
            return None
    return result


def extract_short_id(openalex_id: str) -> str:
    """Extract short ID from OpenAlex full URL."""
    if not openalex_id:
        return None
    return openalex_id.split('/')[-1]


def process_works(input_path: str, output_dir: str) -> None:
    """Process OpenAlex JSONL and generate normalized CSV tables."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    works_data = []
    references_data = []
    authors_data = []
    keywords_data = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                work = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            work_id = extract_short_id(work.get('id'))
            
            works_data.append({
                'work_id': work_id,
                'display_name': work.get('display_name'),
                'doi': work.get('doi'),
                'publication_year': work.get('publication_year'),
                'cited_by_count': work.get('cited_by_count'),
                'primary_location_source': get_nested(work, 'primary_location', 'source', 'display_name')
            })
            
            referenced_works = work.get('referenced_works', []) or []
            for ref_id in referenced_works:
                references_data.append({
                    'work_id': work_id,
                    'reference_id': extract_short_id(ref_id)
                })
            
            authorships = work.get('authorships', []) or []
            for authorship in authorships:
                author = authorship.get('author', {})
                institutions = []
                for inst in authorship.get('institutions', []) or []:
                    if inst and inst.get('display_name'):
                        institutions.append(inst['display_name'])
                
                authors_data.append({
                    'work_id': work_id,
                    'author_id': extract_short_id(author.get('id')) if author else None,
                    'author_name': author.get('display_name') if author else None,
                    'institutions': '; '.join(institutions) if institutions else None,
                    'author_position': authorship.get('author_position'),
                    'is_corresponding': authorship.get('is_corresponding')
                })
            
            keywords = work.get('keywords', []) or []
            for kw in keywords:
                keywords_data.append({
                    'work_id': work_id,
                    'keyword': kw.get('display_name') if isinstance(kw, dict) else kw,
                    'score': kw.get('score') if isinstance(kw, dict) else None,
                    'source': 'keyword'
                })
            
            topics = work.get('topics', []) or []
            for topic in topics:
                keywords_data.append({
                    'work_id': work_id,
                    'keyword': topic.get('display_name') if isinstance(topic, dict) else topic,
                    'score': topic.get('score') if isinstance(topic, dict) else None,
                    'source': 'topic'
                })
    
    works_df = pd.DataFrame(works_data)
    works_df.to_csv(os.path.join(output_dir, 'works_clean.csv'), index=False)
    
    references_df = pd.DataFrame(references_data)
    references_df.to_csv(os.path.join(output_dir, 'work_references.csv'), index=False)
    
    authors_df = pd.DataFrame(authors_data)
    authors_df.to_csv(os.path.join(output_dir, 'work_authors.csv'), index=False)
    
    keywords_df = pd.DataFrame(keywords_data)
    keywords_df.to_csv(os.path.join(output_dir, 'work_keywords.csv'), index=False)
    
    print(f"Processed {len(works_df)} works")
    print(f"Generated {len(references_df)} references")
    print(f"Generated {len(authors_df)} author entries")
    print(f"Generated {len(keywords_df)} keyword/topic entries")
    print(f"Output saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Normalize OpenAlex JSONL to CSV tables')
    parser.add_argument(
        '--input',
        default='data/raw/openalex_works.jsonl',
        help='Path to input JSONL file'
    )
    parser.add_argument(
        '--output',
        default='data/processed',
        help='Output directory for CSV files'
    )
    args = parser.parse_args()
    
    process_works(args.input, args.output)


if __name__ == '__main__':
    main()
