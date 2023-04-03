import logging
import os
import sys

def yes_no_prompt(question):
    while True:
        user_input = input(f"{question} (y/n): ").lower()
        if user_input == 'y':
            return True
        if user_input == 'n':
            return False
        print("Please enter 'y' or 'n'.", file=sys.stderr)

def apply_changes(input_string):
    file_contents = {}
    current_file = None
    current_directory = os.getcwd()

    lines = input_string.split("\n")
    for line in lines:
        if line.startswith("BEGIN_FILE"):
            absolute_path = os.path.abspath(line.split(" ", 1)[1])
            relative_path = os.path.relpath(absolute_path, current_directory)
            if not relative_path.startswith('.') or yes_no_prompt(f'Write {relative_path}?'):
                current_file = relative_path
                file_contents[current_file] = []
        elif line.startswith("END_FILE"):
            current_file = None
        elif line.startswith("EDIT_FILE"):
            parts = line.split(" ", 3)
            absolute_path = os.path.abspath(parts[1])
            relative_path = os.path.relpath(absolute_path, current_directory)
            from_text = parts[3]
            if not relative_path.startswith('.') or yes_no_prompt(f'Edit {relative_path}?'):
                current_file = relative_path
                with open(current_file, "r") as f:
                    original_lines = f.read().split('\n')

                if from_text not in original_lines and from_text.startswith('"') and from_text.endswith('"'):
                    from_text = from_text[1:-1]

                new_lines = []
                while original_lines:
                    original_line = original_lines.pop(0)
                    if original_line.strip() == from_text:
                        break
                    new_lines.append(original_line)

                file_contents[current_file] = new_lines
        elif line.startswith("END_FROM"):
            parts = line.split(" ", 1)
            from_text = parts[1]

            if from_text not in original_lines and from_text.startswith('"') and from_text.endswith('"'):
                from_text = from_text[1:-1]

            while original_lines:
                if original_lines == from_text:
                    break
                original_lines.pop(0)

            file_contentsd[current_file].extend(original_lines)
            current_file = None
        elif current_file in file_contents:
            file_contents[current_file].append(line)

    for filename, content_lines in file_contents.items():
        logging.info('Creating %s', filename)
        with open(filename, "w") as f:
            f.write("\n".join(content_lines))
