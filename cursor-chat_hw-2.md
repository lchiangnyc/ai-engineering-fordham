# homework-2
_Exported on 1/30/2026 at 03:05:15 EST from Cursor (2.4.23)_

---

**User**

Hello there

---

**Cursor**

Hello!  

What would you like to work on in this repo today—homework, debugging, or something else?

---

**User**

I'm looking to resolve an import error

---

**Cursor**

Got it.  

To fix it quickly, I need a bit more detail:
- **What is the exact error message and stack trace?**
- **Which file/cell is causing it, and what are the import lines there?**  

You can paste the error output and the relevant code cell (or file snippet) and I’ll walk through a precise fix.

---

**User**

ImportError                               Traceback (most recent call last)
Cell In[4], line 5
      3 from pydantic import BaseModel, Field
      4 from typing import Literal
----> 5 from google import genai
      6 from google.genai import types
      7 import asyncio

ImportError: cannot import name 'genai' from 'google' (unknown location)

---

**Cursor**

I'll inspect your project setup and the notebook to see how `google` / `genai` is being used, then suggest the precise fix (likely a dependency or import change).

**Cause:** Your environment has a `google` package, but it’s **not** the `google-genai` one that provides `genai`, so `from google import genai` fails.

### Step 1: Make sure `google-genai` is installed in *this* environment
In the same environment/kernel that runs the notebook, run (in a terminal):

```bash
pip show google-genai
```

If it’s missing, install it:

```bash
pip install google-genai
```

(or, for this repo specifically, from the project folder:

```bash
uv sync
```

which will install everything from `pyproject.toml`, including `google-genai`.)

### Step 2: Remove the conflicting `google` package
Still in the same environment, check for the old `google` package:

```bash
pip show google
```

If it exists, uninstall it:

```bash
pip uninstall google
```

(`google-genai` is correct; a top-level `google` meta-package is what causes this conflict.)

### Step 3: Restart the kernel and retry
1. Restart the Jupyter kernel / notebook runtime.
2. Re-run the import cell:

```python
from google import genai
from google.genai import types
```

If you’d like, tell me how you’re running the notebook (VS Code Jupyter / `uv run jupyter` / etc.), and I can give the exact commands/buttons for that setup.

---

**User**

I'll give these a try, thank you

---

**Cursor**

Sounds good.  

If anything still errors after you run those steps (especially after uninstalling `google` and restarting the kernel), paste the new traceback and I’ll drill into it.

---

**User**

I'm not seeing much of a difference

---

**Cursor**

Understood. Let’s pin down what’s still wrong.

### 1. What is the **current** error?
Please rerun the import cell and paste the **full, current traceback** (it might have changed slightly after the package work).

### 2. How are you running the notebook?
Tell me which of these matches your setup:
- **A.** Jupyter inside VS Code / Cursor (using the top-right “Run cell” buttons)
- **B.** A browser Jupyter/Lab started from a terminal (e.g., `jupyter lab` or `uv run jupyter lab`)
- **C.** Something else (describe briefly)

Once I know the exact error text and how you’re launching Jupyter, I can give you step-by-step commands to:
- ensure we’re in the **same environment** that `uv` uses, and
- verify that `google-genai` is installed and the conflicting `google` package is really gone.

---

**User**

---------------------------------------------------------------------------
ImportError                               Traceback (most recent call last)
Cell In[1], line 5
      3 from pydantic import BaseModel, Field
      4 from typing import Literal
----> 5 from google import genai
      6 from google.genai import types
      7 import asyncio

ImportError: cannot import name 'genai' from 'google' (unknown location)

---

**Cursor**

I’ll check which `google`/`google-genai` packages are actually installed in your project environment and then give you an exact fix for this notebook setup.

**Good news:** In your project’s `uv` environment, `google.genai` imports **correctly**. That means the error is coming from the **notebook using a different Python environment**, not from your code.

### What to do

- **Switch the Jupyter kernel to this project’s `.venv`:**  
  In Cursor/VS Code notebook:
  - Click the **kernel / interpreter name** in the top-right of the notebook.
  - In the list, pick the Python that lives under  
    `c:\Users\leona\ai-engineering-fordham\.venv\Scripts\python.exe`  
    (or anything labeled with this project path / `.venv`).
  - Then **restart** the kernel and rerun the import cell.

If you don’t see that interpreter listed, tell me how you’re opening the notebook (Cursor Jupyter, VS Code Python extension, browser Jupyter, etc.), and I’ll give exact steps to register/select the right kernel.

---

**User**

I believe this is Cursor Jupyter in question

---

**Cursor**

Got it, perfect—that helps.

### In Cursor Jupyter, do this:

1. **Open `homework-2.ipynb`** in Cursor (you already have).
2. Look at the **top-right of the notebook editor** for the **kernel / interpreter name** (something like `Python 3.x` or a path).
3. **Click that name** → a list of Python environments will appear.
4. Choose the one whose path includes your project `.venv`, e.g.:  
   `c:\Users\leona\ai-engineering-fordham\.venv\Scripts\python.exe`
5. After switching:
   - Use the notebook menu to **Restart Kernel**.
   - Re-run the first import cell.

If you don’t see any interpreter with `.venv` or `ai-engineering-fordham` in the path, tell me exactly what kernel names you see in that list and I’ll tell you which to pick or how to add the right one.

---

**User**

I think I have the base (Python 3.12) and another for Python 3.14

---

**Cursor**

You’ll want the kernel that matches your **project’s venv**, not just “Python 3.12/3.14”.

### Step 1: Pick the most likely kernel
- Between the two, **pick Python 3.14** (that’s what `uv` is using in this project).
- Restart the kernel after switching, then run this tiny cell:

```python
import sys
print(sys.version)
print(sys.executable)
```

### Step 2: Check the output
- If `sys.executable` path **includes** `ai-engineering-fordham\\.venv\\Scripts\\python.exe`, you’re on the right kernel; re-run your import cell and it should work.
- If it shows something like `C:\Python312\python.exe` or another global path (no `.venv`), tell me that path and I’ll walk you through making Cursor use the project’s `.venv` kernel.

---

**User**

But 3.14 requires I install ipykernel. How do I approach that?

---

**Cursor**

You’re right: to use the **3.14 project env** as a Jupyter kernel, you need `ipykernel` installed *in that env* and the kernel registered.

Given your project setup, here’s the clean path:

### 1. Install dependencies (including `ipykernel`) into the venv

From a terminal in the project folder `c:\Users\leona\ai-engineering-fordham`:

```bash
uv sync
```

Your `pyproject.toml` already includes `ipykernel`, so this puts it into `.venv`.

### 2. Register the venv as a Jupyter kernel

Still in the same folder:

```bash
uv run python -m ipykernel install --user --name ai-eng-fordham-3-14 --display-name "Python 3.14 (ai-eng-fordham)"
```

### 3. Select this kernel in Cursor

- In `homework-2.ipynb`, click the kernel name top-right.
- Pick **“Python 3.14 (ai-eng-fordham)”**.
- Restart kernel and rerun the import cell.

If any of these commands error, paste the exact output and I’ll adjust.

---

**User**

I'm seeing progress. Next up: how do I create a .gitignore for this directory?

---

**Cursor**

I’ll set up a sensible `.gitignore` for a Python/uv + Jupyter project in this repo and add entries for env files and notebooks’ temp artifacts.

You now have a `.gitignore` in this repo that ignores:

- **Virtual env and Python cruft**: `.venv/`, `__pycache__/`, `*.pyc`
- **Notebook + editor noise**: `.ipynb_checkpoints/`, `.vscode/`, `.idea/`, `.cursor/`
- **Secrets**: `.env`, `keys.env`
- **Misc**: `.DS_Store`, `Thumbs.db`, `.python-version`  

You’re safe to `git add` without accidentally committing your env or keys.

---

**User**

Litellm call returns an empty Response

---

**Cursor**

To debug this I need to see exactly how you’re calling it and what “empty” means in your case.

### First, can you show me:

1. **The code cell** where you call LiteLLM (especially the `litellm.completion(...)` line and how you print the result).  
2. **What’s printed** when you run:

```python
import litellm
response = litellm.completion(
    model="gpt-5-mini",  # or whatever you're using
    messages=[{"role": "user", "content": "Say 'API working!' and nothing else."}],
    max_tokens=20
)
print("raw response:", response)
print("choices:", getattr(response, "choices", None))
if getattr(response, "choices", None):
    print("first choice message:", response.choices[0].message)
    print("first choice content:", response.choices[0].message.content)
```

Paste that output here.

### Common causes to check while you run that

- **Access pattern mismatch**:  
  In some setups you need `response['choices'][0]['message']['content']` (dict-style) instead of attribute-style, depending on your LiteLLM config.
- **Silent error inside `response`**:  
  Sometimes `response` has an `error` or `usage` field but `choices` is empty. Printing `response` fully will reveal this.
- **Wrong model / provider config**:  
  If `"gpt-5-mini"` isn’t valid for your configured provider, the call may fail or return an unexpected structure.

Once I see your call and that debug output, I can tell you exactly what to change (print access, model name, or config).

---

**User**

Here's what I got:

raw response: ModelResponse(id='chatcmpl-D2fXvVs24ZwoMJyPDV5yBmZ48webR', created=1769528731, model='gpt-5-mini-2025-08-07', object='chat.completion', system_fingerprint=None, choices=[Choices(finish_reason='length', index=0, message=Message(content='', role='assistant', tool_calls=None, function_call=None, provider_specific_fields={'refusal': None}, annotations=[]), provider_specific_fields={})], usage=Usage(completion_tokens=30, prompt_tokens=15, total_tokens=45, completion_tokens_details=CompletionTokensDetailsWrapper(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=30, rejected_prediction_tokens=0, text_tokens=None, image_tokens=None), prompt_tokens_details=PromptTokensDetailsWrapper(audio_tokens=0, cached_tokens=0, text_tokens=None, image_tokens=None)), service_tier='default')
choices: [Choices(finish_reason='length', index=0, message=Message(content='', role='assistant', tool_calls=None, function_call=None, provider_specific_fields={'refusal': None}, annotations=[]), provider_specific_fields={})]
first choice message: Message(content='', role='assistant', tool_calls=None, function_call=None, provider_specific_fields={'refusal': None}, annotations=[])
first choice content: 

---

**Cursor**

Great, that output is very informative.

### What’s happening

From the response:

- **`finish_reason='length'`** → The model stopped because it hit your `max_tokens` limit.
- **`completion_tokens=30`** and **`completion_tokens_details.reasoning_tokens=30`**, **`text_tokens=None`** → All 30 completion tokens were used for **internal reasoning tokens**, and **zero tokens** were used for visible text.
- So **`message.content` is empty** because the model never got to emit any user-visible text before you cut it off.

This is typical behavior for **reasoning-style models**: they can spend some of the budget on hidden “thinking” tokens before producing any output. With `max_tokens=30`, your entire budget was consumed by reasoning.

### How to fix it

In your call:

```python
response = litellm.completion(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": "Say 'API working!' and nothing else."}],
    max_tokens=30,
)
print(response.choices[0].message.content)
```

Try one of these:

1. **Increase `max_tokens` so the model has room to output text:**

```python
response = litellm.completion(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": "Say 'API working!' and nothing else."}],
    max_tokens=200,  # or just remove this arg to use default
)
print(response.choices[0].message.content)
```

2. **Optionally, use a non-reasoning/chat model alias** (if your LiteLLM config has one, e.g. `"gpt-4.1-mini"` or similar), which won’t burn as many reasoning tokens.

If you bump `max_tokens` and still get empty content, paste the new `raw response:` line again and we’ll interpret it, but with 200+ tokens you should see `"API working!"` in `message.content`.

---

**User**

I have a Cell that won't run: 

---

**Cursor**

To troubleshoot it, I need a bit more detail.

Please paste:
- **The full error message / traceback** you see for that cell.
- **The code in that cell** (or at least the relevant part).

With those two, I can explain exactly why it’s failing and what to change.

---

**User**

@homework-2.ipynb (1-16) 

---

**Cursor**

Looking at that cell, the code itself is fine; the usual reason it “won’t run” here is:

### Most likely error

You’re probably getting something like:

```text
NameError: name 'Movie' is not defined
```

because this line:

```python
def generate_poster_prompt(movie: Movie) -> str:
```

requires `Movie` to already exist in the current kernel session.

### How to fix

- **Option 1 (recommended for the homework):**  
  In your notebook, re‑run the cells **in order from the top**, making sure you run the cell that defines the `Movie` class (Task 2) **before** you run the Task 8a cell.

- **Option 2 (if you want to avoid the dependency when defining):**  
  Change the signature to use a string annotation so it doesn’t need `Movie` at definition time:
  ```python
  def generate_poster_prompt(movie: "Movie") -> str:
      ...
  ```
  (still make sure `Movie` is defined before you actually call `generate_poster_prompt`).

If the error you see is different from a `NameError` about `Movie`, paste the exact traceback and I’ll interpret that one specifically.

---

**User**

Notebook stalled out, referencing file length

---

**Cursor**

Likely your notebook hit a heavy cell (lots of output / big objects) and Cursor is struggling with the `.ipynb` size or a long‑running execution.

### Quick recovery steps

- **1. Interrupt the kernel**
  - In Cursor’s notebook UI, click **“Stop” / square icon** or use the command palette for **“Interrupt Kernel”**.
  - Wait until the cell gets the `KeyboardInterrupt` or the `[*]` on the left turns into a number.

- **2. Save + close + reopen**
  - Once it’s no longer running, **save** the notebook.
  - Close `homework-2.ipynb`, then reopen it; this often clears UI stall issues.

- **3. Clear outputs of heavy cells**
  - Any cells that:
    - Print **huge responses**, or
    - Print per‑token logprobs in large loops  
  can bloat the file.
  - Use the notebook menu: **“Clear All Outputs”** (or right‑click individual cells → **“Clear Cell Output”**), then save again.

- **4. Re-run cells in small chunks**
  - Re-run only up to the section you’re working on (e.g., Tasks 1–4), not the entire notebook at once.
  - For logprob / debugging cells, **comment out** or shorten loops (e.g., only print the first 5 tokens) before re-running.

### If there’s an explicit “file length” message

If you see a specific error text (e.g., “file length exceeds …”, “too large to open”, etc.), copy–paste that exact message here and I’ll give a tailored fix (possibly trimming outputs or splitting the notebook).

---

**User**

Hi again - I'm kicking an error, traceback below

23:40:10 - LiteLLM:ERROR: utils.py:1151 - litellm.utils.py::function_setup() - [Non-Blocking] Error in function_setup
Traceback (most recent call last):
  File "c:\Users\leona\ai-engineering-fordham\.venv\Lib\site-packages\litellm\utils.py", line 765, in function_setup
    custom_llm_setup()
    ~~~~~~~~~~~~~~~~^^
  File "c:\Users\leona\ai-engineering-fordham\.venv\Lib\site-packages\litellm\utils.py", line 492, in custom_llm_setup
    for custom_llm in litellm.custom_provider_map:
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'litellm' has no attribute 'custom_provider_map'
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
Cell In[16], line 4
      1 # Task 1b: Verify API keys (5 pts)
      2 # Make a simple test call to verify your OpenAI API key works
----> 4 response_1b = litellm.completion(
      5     model="gpt-5-mini",
      6     messages=[{"role": "user", "content": "Say 'API working!' and nothing else."}],
      7     max_tokens=20
      8     )
      9 print(response_1b.choices[0].message.content)

File c:\Users\leona\ai-engineering-fordham\.venv\Lib\site-packages\litellm\utils.py:1740, in client.<locals>.wrapper(*args, **kwargs)
   1736 if logging_obj:
   1737     logging_obj.failure_handler(
   1738         e, traceback_exception, start_time, end_time
   1739     )  # DO NOT MAKE THREADED - router retry fallback relies on this!
-> 1740 raise e

File c:\Users\leona\ai-engineering-fordham\.venv\Lib\site-packages\litellm\utils.py:1449, in client.<locals>.wrapper(*args, **kwargs)
   1447 try:
   1448     if logging_obj is None:
-> 1449         logging_obj, kwargs = function_setup(
   1450             original_function.__name__, rules_obj, start_time, *args, **kwargs
   1451         )
   1452     ## LOAD CREDENTIALS
   1453     load_credentials_from_list(kwargs)

File c:\Users\leona\ai-engineering-fordham\.venv\Lib\site-packages\litellm\utils.py:1154, in function_setup(original_function, rules_obj, start_time, *args, **kwargs)
   1150 except Exception as e:
   1151     verbose_logger.exception(
   1152         "litellm.utils.py::function_setup() - [Non-Blocking] Error in function_setup"
   1153     )
-> 1154     raise e

File c:\Users\leona\ai-engineering-fordham\.venv\Lib\site-packages\litellm\utils.py:765, in function_setup(original_function, rules_obj, start_time, *args, **kwargs)
    762 global callback_list, add_breadcrumb, user_logger_fn, Logging
    764 ## CUSTOM LLM SETUP ##
--> 765 custom_llm_setup()
    767 ## GET APPLIED GUARDRAILS
    768 applied_guardrails = get_applied_guardrails(kwargs)

File c:\Users\leona\ai-engineering-fordham\.venv\Lib\site-packages\litellm\utils.py:492, in custom_llm_setup()
    488 def custom_llm_setup():
    489     """
    490     Add custom_llm provider to provider list
    491     """
--> 492     for custom_llm in litellm.custom_provider_map:
    493         if custom_llm["provider"] not in litellm.provider_list:
    494             litellm.provider_list.append(custom_llm["provider"])

AttributeError: module 'litellm' has no attribute 'custom_provider_map'

---

**Cursor**

This is a **version mismatch / corrupt install** issue with LiteLLM. The installed code is calling `litellm.custom_provider_map`, but that attribute doesn't exist in your current installation—likely caused by a partial update or bytecode caching problem.

### Fix: Reinstall LiteLLM cleanly

Run these commands in a terminal from your project folder (`c:\Users\leona\ai-engineering-fordham`):

```bash
uv pip uninstall litellm
uv pip install litellm
```

Or, to ensure everything is fresh:

```bash
uv sync --reinstall-package litellm
```

### Then:

1. **Restart the Jupyter kernel** (important—old module references stay in memory).
2. Re-run the import cell and the Task 1b cell.

If it still errors after that, try a full environment refresh:

```bash
uv sync --refresh
```

…then restart the kernel and retry.

Let me know what happens after the reinstall.

---

**User**

Reinstallation successful. Thank you for all your help

---

**Cursor**

Great to hear! Glad everything's working now.

Good luck with the rest of the homework—looks like you've already generated some movie posters. If you hit any other snags, feel free to ask.

