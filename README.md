# gptcli

A command line program to interact with GPT models.

## Features

- Edit existing files with the help of the GPT model by describing the changes in plain English.
- Store the history of prompts and responses in a local SQLite database.

## Usage

1. Set the `OPENAI_API_KEY` environment variable to your OpenAI API key.
2. Run the script with the desired options and arguments.

### Basic usage

```
hey_gpt "your prompt here"
```

### Using a specific model and temperature

```
hey_gpt "your prompt here" --model gpt-4 --temperature 0.7
```

### Editing an existing file

```
hey_gpt --edit FILE
```

Then, write a description of the desired changes in plain English.

## Example

To edit an existing file called `example.txt`, run:

```
hey_gpt --edit example.txt
```

In the text editor that opens, describe the changes you want to make to the file. For example:

```
I'd like to change the text in example.txt to have a more positive tone.
```

After you save and close the text editor, the GPT model will generate a new version of the file with the requested changes.

## Features proposed by GPT-4

* Batch processing of multiple files for editing or generating content.
* Integration with popular version control systems for easy collaboration.
* Customizable output formatting for different use cases.
* Optional real-time interaction mode for faster feedback and adjustments.
* Multilingual support for interacting with GPT models in different languages.
* User-defined templates for generating content in specific formats or structures.
* Integration with cloud storage services for direct file access and management.
* Support for automatically summarizing long pieces of text or documents.
* Built-in translation features to quickly translate content between languages.
* Integration with task management and productivity tools for seamless workflows.
* Support for generating content based on social media platform-specific guidelines.
* Ability to schedule content generation for future times or recurring intervals.
* Integration with machine learning libraries for custom model training and fine-tuning.
* Built-in plagiarism detection to ensure the originality of generated content.
* Support for generating content based on user personas, profiles, or target audiences.
* Integration with content management systems for easy publishing and distribution.
* Support for generating content in various file formats, such as PDF, Word, or Markdown.
