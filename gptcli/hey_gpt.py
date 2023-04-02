import argparse
import difflib
import json
import logging
import os
import pathlib
import re
import sqlite3
import sys
import tempfile

import requests

import gptcli.logging

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

def apply_changes(input_string):
    file_contents = {}
    current_file = None
    diff = False

    current_directory = os.getcwd()

    lines = input_string.split("\n")
    for line in lines:
        if line.startswith("BEGIN_FILE"):
            absolute_path = os.path.abspath(line.split(" ", 1)[1])
            relative_path = os.path.relpath(absolute_path, current_directory)
            if not relative_path.startswith('.'):
                current_file = relative_path
                file_contents[current_file] = []
        elif line.startswith("END_FILE"):
            current_file = None
        else:
            if diff:
                diff_lines.append(line)
            elif current_file in file_contents:
                file_contents[current_file].append(line)

    for filename, content_lines in file_contents.items():
        logging.info('Creating %s', filename)
        with open(filename, "w") as f:
            f.write("\n".join(content_lines))

def apply_diff(file_contents, diff_lines):
    unified_diff = "\n".join(diff_lines)
    diff = list(difflib.unified_diff_to_file(file_contents, unified_diff))
    filename = re.search(r'--- (.+)', unified_diff).group(1)
    file_contents[filename] = diff

def main():
    gptcli.logging.setup()

    parser = argparse.ArgumentParser(description='Interact with OpenAI API using different models and temperature settings.')
    parser.add_argument('prompt', nargs='*', help='The prompt for the model.')
    parser.add_argument('--no-prompt-prefix', action='store_true', help='Don\'t add the prompt prefix')
    parser.add_argument('--model', default='gpt-4', help='The model to use. (default: gpt-4)')
    parser.add_argument('--temperature', type=float, default=0.7, help='The temperature setting for the model. (default: 0.7)')
    parser.add_argument('--edit', metavar='FILENAME', help='Edit a file with the given filename.')
    args = parser.parse_args()

    if args.prompt:
        prompt = ' '.join(args.prompt)
    else:
        prompt = sys.stdin.read().strip()

    if args.edit:
        with open(args.edit, 'r') as f:
            file_contents = f.read()
        prompt = f"BEGIN_FILE {args.edit}\n{file_contents}\nEND_FILE\nI wish to change the above file, {args.edit}, as described here:\n{prompt}"

    if not args.no_prompt_prefix:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(script_dir, 'prompt_prefix.txt'), 'r') as f:
            prompt_prefix = f.read().strip()
        prompt = prompt_prefix + prompt

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

    db_path = pathlib.Path.home() / '.local/share/hey_gpt/history.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    create_table(conn)
    insert_history(conn, prompt, response_text)
    conn.close()

    apply_changes(response_text)

if __name__ == "__main__":
    main()
