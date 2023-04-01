#!/usr/bin/env python3

import argparse
import json
import os
import sys
import sqlite3
from pathlib import Path

import requests

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL
        )
    ''')
    conn.commit()

def insert_history(conn, prompt, response):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (prompt, response) VALUES (?, ?)
    ''', (prompt, response))
    conn.commit()

def stream_response(response):
    content = ''
    for chunk in response.iter_content(chunk_size=None):
        for data_element in chunk.split(b'\n\n'):
            if not data_element.startswith(b'data: '):
                continue
            data_element = data_element[6:]
            if data_element == b'[DONE]':
                break
            try:
                json_chunk = json.loads(data_element)
            except Exception:
                print(f'Failed chunk: {data_element}', file=sys.stderr)
                raise
            try:
                content_chunk = json_chunk['choices'][0]['delta']['content']
            except KeyError:
                continue
            sys.stdout.write(content_chunk)
            sys.stdout.flush()
            content += content_chunk
    return content

def main():
    parser = argparse.ArgumentParser(description='Interact with OpenAI API using different models and temperature settings.')
    parser.add_argument('prompt', nargs='*', help='The prompt for the model.')
    parser.add_argument('--model', default='gpt-4', help='The model to use. (default: gpt-4)')
    parser.add_argument('--temperature', type=float, default=0.7, help='The temperature setting for the model. (default: 0.7)')

    args = parser.parse_args()

    if args.prompt:
        prompt = ' '.join(args.prompt)
    else:
        prompt = sys.stdin.read().strip()

    if not prompt:
        return

    api_key = os.environ["OPENAI_API_KEY"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": args.model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": args.temperature,
        "stream": True,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        data=json.dumps(data),
        stream=True
    )

    response_text = stream_response(response)

    db_path = Path.home() / '.local/share/hey_gpt/history.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    create_table(conn)
    insert_history(conn, prompt, response_text)
    conn.close()

if __name__ == "__main__":
    main()
