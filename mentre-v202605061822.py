# Mentre AI-Powered Study Tool

# James Bommentre & Leonard Chiang,
    # in conjunction with ChatGPT and Cursor Agent

# Wed 06 May 2026
# ISGB 79AM - RAG and Context Engineering
# Dr. Apostolos Filippas


from pydantic import BaseModel, Field

from pypdf import PasswordType, PdfReader
import requests
from bs4 import BeautifulSoup

import litellm

import gradio as gr

# -----------------------------
# 1. Preparing LLM output structure
# -----------------------------

# Defining Pydantic schema 
class StudySummary(BaseModel):
    title: str = Field(
        description = "A short title for the document")
    summary: str = Field(
        description = "A clear, student-friendly summary")
    key_concepts: list[str] = Field(
        description = "Important concepts, people, events, terms, entities, etc.")
    study_questions: list[str] = Field(
        description = "Questions to improve recall and understanding")


# -----------------------------
# 2. Generic scraper
# -----------------------------

# Applying BeautifulSoup to webpage
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # remove scripts and styles
        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text(separator=" ")

        # clean up whitespace
        lines = [line.strip() for line in text.splitlines()]
        text = " ".join(line for line in lines if line)

        return text[:100000]  # limit length for speed

    except Exception as e:
        return f"Error fetching URL: {e}"


def extract_text_from_upload(path: str) -> str:
    """Read plaintext or extract text from a PDF (same length cap as URL scraping)."""
    max_chars = 100000
    lower = path.lower()
    if lower.endswith(".pdf"):
        try:
            reader = PdfReader(path)
            if reader.is_encrypted and reader.decrypt("") == PasswordType.NOT_DECRYPTED:
                raise ValueError(
                    "This PDF is password-protected. "
                    "Save an unlocked copy or use a .txt export."
                )
            chunks: list[str] = []
            for page in reader.pages:
                chunks.append(page.extract_text() or "")
            text = "\n".join(chunks)
            lines = [line.strip() for line in text.splitlines()]
            text = " ".join(line for line in lines if line)
            if not text:
                raise ValueError("No extractable text found in PDF (may be scanned images).")
            return text[:max_chars]
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Could not read PDF: {e}") from e
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()[:max_chars]


# -----------------------------
# 3. Summarizing text via LLM
# -----------------------------

# LiteLLM Call #1: Soliciting summary
def generate_summary(text):
    response1 = litellm.completion(
        model = "gpt-5-nano",
        messages = [
            {
                "role" : "user",
                "content": f"""
                    You are an AI study assistant.

                    Read the document below and create a study-friendly summary.

                    Return your answer in this exact format:

                    SUMMARY:\n
                        [Clear and concise paragraph summary, no more than 3 sentences]\n\n

                    KEY CONCEPTS:\n
                        - Concept 1\n
                        - Concept 2\n
                        - Concept 3\n\n

                    STUDY QUESTIONS:\n
                        1. Question 1\n
                        2. Question 2\n
                        3. Question 3\n

                    Document:
                        {text}
                """
                }
            ],
        )

    return response1.choices[0].message.content


# -----------------------------
# 4. Core program logic
# -----------------------------


# Calling functions
def study_tool(text_input, file_input, url_input):
    final_text = ""

    # Priority: file > URL > text
    if file_input is not None:
        try:
            final_text = extract_text_from_upload(file_input.name)
        except ValueError as e:
            return str(e), "", "", ""

    elif url_input and len(url_input.strip()) > 0:
        final_text = extract_text_from_url(url_input)

    elif text_input and len(text_input.strip()) > 0:
        final_text = text_input

    else:
        return (
            "Please paste text, upload a file, or enter a URL.",
            "",
            "",
            "",
        )

    summary = generate_summary(final_text)
    mermaid_code = generate_mermaid(final_text)
    mermaid_visual = render_mermaid_html(mermaid_code)

    instructions = """
        ### Diagram Help

        The visual diagram should appear above.

        If it does not load correctly: copy the Mermaid code, then paste into the Mermaid Live Editor (https://mermaid.live).
    """

    return summary, mermaid_code, mermaid_visual, instructions


# -----------------------------
# 5. Diagramming with Mermaid
# -----------------------------

# LiteLLM Call #2: Generating Mermaid-compatible syntax
def generate_mermaid(text):
    response2 = litellm.completion(
        model = "gpt-5-nano",
        messages = [
            {
                "role": "user",
                "content": f"""
                        Create Mermaid.js flowchart syntax that visually summarizes the document below.

                        Rules:
                            - Return only Mermaid code
                            - Start exactly with: flowchart TD
                            - Keep it simple and readable: Use 5 to 8 nodes maximum
                            - Show the most important concepts and relationships
                            - Do not use markdown backticks
                            - Use short node labels, avoiding special characters
                            - Do not explain the diagram
                        
                        Document:
                            {text}
                    """
                }
            ],
        )

    mermaid_code = str(response2.choices[0].message.content)

    # Clean common formatting mistakes
    mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()

    return mermaid_code

# Rendering Mermaid diagram in-page
def render_mermaid_html(mermaid_code):
    mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()

    html = f"""
    <iframe
        style="width: 100%; height: 500px; border: 1px solid #444; border-radius: 8px;"
        srcdoc='
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>
                mermaid.initialize({{ startOnLoad: true, theme: "dark" }});
            </script>
        </head>
        <body style="background-color:#1e1e1e; color:white;">
            <div class="mermaid">
                {mermaid_code}
            </div>
        </body>
        </html>
        '
    ></iframe>
    """

    return html


# -----------------------------
# 6. User interface
# -----------------------------

# Defining Gradio elements
app = gr.Interface(
    fn = study_tool,
    inputs = [
        gr.Textbox(
            label = "Paste your document text here:",
            lines = 10,
            placeholder = "Paste an article, class notes, textbook section, or document text..."
            ),
        gr.File(
            label = "Or upload a plaintext file or PDF:",
            file_types = [".txt", ".pdf"]
            ),
        gr.Textbox(
            label = "Or enter a URL:",
            placeholder = "https://example.com/article"
            )
        ],
    outputs = [
        gr.Markdown(label = "Study-Ready AI Summary"),
        gr.Code(label = "Mermaid Diagram Code", language = "markdown"),
        gr.HTML(label = "Visual Mermaid Diagram"),
        gr.Markdown(label = "Diagram Help")
        ],
    title = "Mentre Study Tool by James Bommentre and Leonard Chiang",
    description = "Put in your text content and get a study-friendly summary with key concepts and questions, plus convenient Mermaid visual!"
    )


if __name__ == "__main__":
    app.launch(share = True)