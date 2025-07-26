# DepoIndex: AI-Powered Deposition Topic Indexer

DepoIndex is an automated tool that reads a legal deposition transcript, uses AI to identify distinct topics of discussion, and generates a clean, paginated Table of Contents. This eliminates the need for manual scanning and allows legal professionals to navigate lengthy documents with ease.

REPLACE WITH YOUR API KEY IN CASE API QUOTA EXHAUSTED TO PREVENT RUNTIME FAILURE, FOR BOTH VALIDATION NB and SCRIPT python file

## Project files
- **script.py**: The main engine that reads the PDF, cleans the text, calls the AI, and generates the final output files.

- **toc.docx**: The final, human-readable Table of Contents, formatted as a Word document.

- **topics.json:** A raw data file containing the structured output from the AI. This file is used by the validation notebook.

- **validation.ipynb**: A Jupyter Notebook used to test the AI's performance and accuracy.

- **requirements.txt**: A list of all the Python libraries needed to run the project.

- **Dockerfile**: A configuration file to build a portable Docker container for deployment.

## Features

- **Automated Topic Extraction:** Uses the Gemini AI model to intelligently segment the deposition by subject.
- **Precise Indexing:** Identifies the exact page and line number where each new topic begins.
- **Multiple Output Formats:** Generates the Table of Contents as both a clean Markdown (`.md`) file and a Word-compatible (`.docx`) document.
- **Containerized & Portable:** Packaged with Docker to ensure it runs consistently in any environment.

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/) must be installed and running on your system.

## Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/DepoIndex.git](https://github.com/your-username/DepoIndex.git)
    cd DepoIndex
    ```

2.  **Place Your Files:**
    -   Make sure your main Python script (e.g., `script.py`), your `requirements.txt`, and your input PDF (`DepostionForPersisYu_LinkPDF.pdf`) are in the project folder.

3.  **Build the Docker Image:**
    From your project's root directory, run the following command. This will build the Docker image and tag it as `depoindex`.
    ```bash
    docker build -t depoindex .
    ```

## Usage

To run the script, you will execute a `docker run` command. This command starts a new container from your image and mounts a local `output` directory to it, so the generated files (`toc.md`, `toc.docx`) are saved directly to your host machine.

1.  **Create an Output Directory:**
    ```bash
    mkdir output
    ```

2.  **Run the Container:**
    ```bash
    docker run --rm -v "$(pwd)/output:/app/output" depoindex
    ```
    * `--rm`: Automatically removes the container when it finishes running.
    * `-v "$(pwd)/output:/app/output"`: Mounts your newly created `output` folder into the container's `/app/output` directory. You will need to modify your Python script to save the output files to this `/app/output` path.

After the script finishes, your generated Table of Contents files will be available in the `output` folder on your local machine.