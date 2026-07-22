"""Build metadata.json cho HD_PATIENT_FORM.

Source files (pretty, dễ edit):
  - sources/loadQuery.sql        — SELECT chính

Run: python _build.py
Output: metadata.json (đã merge nội dung từ sources/* vào)
"""
import json
import os

PAGE_DIR = os.path.dirname(os.path.abspath(__file__))
METADATA_PATH = os.path.join(PAGE_DIR, 'metadata.json')
SOURCES_DIR = os.path.join(PAGE_DIR, 'sources')


def read_text(filename):
    path = os.path.join(SOURCES_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def main():
    load_query = read_text('loadQuery.sql')

    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    meta['dataSource']['loadQuery'] = load_query

    with open(METADATA_PATH, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f'OK - wrote {METADATA_PATH}')
    print(f'  loadQuery   {len(load_query)} chars')


if __name__ == '__main__':
    main()
