import argparse
import json
import logging
import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import tempfile

import requests

import gptcli.apply
import gptcli.history
import gptcli.logging

def stream_response(response):
    content = ''
    try:
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
    except Exception:
        mig.logging.exception('Response truncated due to error')
    return content

def get_editor():
    return os.environ.get("EDITOR", "vi")

def get_prompt_from_editor():
    with tempfile.NamedTemporaryFile(mode="w+t", suffix=".txt", delete=False) as temp_file:
        temp_file.close()
        try:
            subprocess.run([get_editor(), temp_file.name], check=True)
            with open(temp_file.name, "r") as f:
                return f.read().strip()
        finally:
            os.unlink(temp_file.name)

def main():
    gptcli.logging.setup()

    parser = argparse.ArgumentParser(description='Interact with OpenAI API using different models and temperature settings.')
    parser.add_argument('prompt', nargs='*', help='The prompt for the model.')
    parser.add_argument('--no-system-prompt', action='store_true', help='Don\'t add the system prompt')
    parser.add_argument('--model', default='gpt-4', help='The model to use. (default: gpt-4)')
    parser.add_argument('--temperature', type=float, default=0.7, help='The temperature setting for the model. (default: 0.7)')
    parser.add_argument('--edit', metavar='FILENAME', nargs='+', help='Edit a file or files with the given filename(s).')
    args = parser.parse_args()

    db_path = pathlib.Path.home() / '.local/share/hey_gpt/history.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    gptcli.history.create_table(conn)

    if args.prompt:
        prompt = ' '.join(args.prompt)
    elif sys.stdin.isatty():
        prompt = get_prompt_from_editor()
        if not prompt:
            print("Error: Empty prompt", file=sys.stderr)
            sys.exit(1)
    else:
        prompt = sys.stdin.read().strip()

    if args.edit:
        file_contents_list = []
        for edit_filename in args.edit:
            with open(edit_filename, 'r') as f:
                file_contents = f.read()
            file_contents_list.append(f"BEGIN_FILE {edit_filename}\n{file_contents}\nEND_FILE")

        files_contents_str = "\n".join(file_contents_list)
        if len(args.edit) > 1:
            file_description = f"the above files, {', '.join(args.edit)},"
        else:
            file_description = f"the above file, {args.edit[0]},"
        prompt = f"{files_contents_str}\nI wish to change {file_description} as described here:\n{prompt}"

    if not prompt:
        return

    api_key = os.environ["OPENAI_API_KEY"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    messages = []

    if not args.no_system_prompt:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(script_dir, 'prompt_prefix.txt'), 'r') as f:
            messages.append({"role": "system", "content": f.read().strip()})

    messages.append({"role": "user", "content": prompt})

    data = {
        "model": args.model,
        "messages": messages,
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

    if not response_text.endswith('\n'):
        sys.stdout.write('\n')

    gptcli.history.insert(conn, prompt, response_text)
    conn.close()

    gptcli.apply.apply_changes(response_text)

if __name__ == "__main__":
    main()
