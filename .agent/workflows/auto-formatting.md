---
description: Ensure we are linting as we go. Trying to reduce the amount of bugs when running tests.
---

### **Workflow: Auto-Formatting**
* **Self-Correction:** If you write Python code, assume it is unformatted.
* **Mandatory Action:** Before finalizing your response, you generally should run `black .` or `ruff check --fix .` on the file you just edited to ensure compliance.
* **Verification:** Ensure the code passes the 88-char limit check before presenting it to the user.
