# gptcli

A command line program to interact with GPT models.

## Features

- Interact with OpenAI API using different models and temperature settings.
- Optionally add a prompt prefix to your text.
- Edit existing files with the help of the GPT model by describing the changes in plain English.
- Store the history of prompts and responses in a local SQLite database.

## Usage

1. Set the `OPENAI_API_KEY` environment variable to your OpenAI API key.
2. Run the script with the desired options and arguments.

### Basic usage

```
python gptcli/hey_gpt.py "your prompt here"
```

### Using a specific model and temperature

```
python gptcli/hey_gpt.py "your prompt here" --model gpt-4 --temperature 0.7
```

### Editing an existing file

```
python gptcli/hey_gpt.py --edit FILE
```

Then, write a description of the desired changes in plain English.

## Example

To edit an existing file called `example.txt`, run:

```
python gptcli/hey_gpt.py --edit example.txt
```

In the text editor that opens, describe the changes you want to make to the file. For example:

```
I'd like to change the text in example.txt to have a more positive tone.
```

After you save and close the text editor, the GPT model will generate a new version of the file with the requested changes.
