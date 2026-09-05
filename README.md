## Tool Inventory

| Tool                                                                                           | Inputs                                                                       | Returns      | Purpose                                                                                                                                                       |
| ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `search_listings(description: str, size: str \| None = None, max_price: float \| None = None)` | Natural language description, optional clothing size, optional maximum price | `list[dict]` | Searches the mock thrift listings using keyword matching while applying optional size and price filters. Returns matching listings ranked by relevance.       |
| `suggest_outfit(new_item: dict, wardrobe: dict)`                                               | Selected listing and user's wardrobe                                         | `str`        | Uses Groq's Llama 3.3 70B model to generate one or two outfit suggestions that combine the selected thrift item with clothing already in the user's wardrobe. |
| `create_fit_card(outfit: str, new_item: dict)`                                                 | Outfit recommendation and selected listing                                   | `str`        | Uses Groq's Llama 3.3 70B model to generate a short social-media style caption describing the completed outfit.                                               |

---

# Interaction Walkthrough

### User query:

> "I'm looking for a vintage denim jacket in size M under $40."

### Step 1 — Tool called

- **Tool:** `search_listings()`
- **Input:**
  - description = `"vintage denim jacket"`
  - size = `"M"`
  - max_price = `40`

- **Why this tool:**
  - The agent first searches the listing database for matching secondhand clothing that satisfies the user's filters.

- **Output:**
  - A ranked list of matching listings. The top result is selected for the recommendation workflow.

---

### Step 2 — Tool called

- **Tool:** `suggest_outfit()`
- **Input:**
  - new_item = selected denim jacket listing
  - wardrobe = user's wardrobe dictionary

- **Why this tool:**
  - After finding a listing, the agent generates outfit recommendations that incorporate clothing the user already owns.

- **Output:**
  - One or two outfit suggestions describing how to style the denim jacket with existing wardrobe pieces.

---

### Step 3 — Tool called

- **Tool:** `create_fit_card()`
- **Input:**
  - outfit = generated outfit recommendation
  - new_item = selected denim jacket listing

- **Why this tool:**
  - Converts the outfit recommendation into an engaging social media style caption that highlights the thrift find.

- **Output:**
  - A 2–4 sentence caption mentioning the thrift item, its price, and marketplace.

---

## Final output to user

Recommended Listing:

- Vintage Denim Jacket
- Size: M
- Price: $35

Suggested Outfit:

Pair the vintage denim jacket with your white graphic tee, black straight-leg jeans, and white sneakers for an everyday casual look. Finish with your silver chain necklace to add a little personality without overpowering the outfit.

Fit Card:

Just picked up this Vintage Denim Jacket for only $35 on Depop and it instantly pulled the whole outfit together. Thrift finds like this make everyday fits feel unique without breaking the budget.

---

# Error Handling and Fail Points

| Tool              | Failure mode                               | Agent response                                                                                                                 |
| ----------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `search_listings` | No listings match the search filters.      | Returns an empty list and informs the user that no matching items were found, encouraging them to broaden the search criteria. |
| `suggest_outfit`  | Wardrobe is empty or missing.              | Generates outfit ideas using common wardrobe basics instead of personalized recommendations.                                   |
| `create_fit_card` | Outfit recommendation is missing or empty. | Returns `"Unable to generate a Fit Card because the outfit recommendation is missing."` instead of calling the language model. |

---

# AI Usage

I used ChatGPT in two ways during this project.

**Bug fixes for `search_listings`:** I described the bug where the search function crashed on listings with missing or `None` fields and asked ChatGPT for a fix. The suggested fix handled empty strings but didn't account for `None` values coming directly from the data loader. I modified it to use `or ""` fallbacks on each field before joining them into the searchable text, so `None` values are coerced to empty strings before any string operations run.

**Coding the agent loop from the planning document:** I had an ASCII flowchart in my planning document showing how the three tools connect in sequence. I pasted that chart into ChatGPT and asked it to scaffold the `run_agent` function. The generated code defaulted to the OpenAI client and GPT model names. Before using it I updated every API call to use the Groq client and `llama-3.3-70b-versatile` to match the rest of the project, and adjusted the response access pattern from `response.output_text` to `response.choices[0].message.content`.

---

# Spec Reflection

### One way planning.md helped during implementation:

Planning the workflow before coding made it easier to separate the project into three independent tools. Since each tool performs one specific task, I was able to test the search functionality, outfit generation, and caption generation independently before connecting them through the agent loop.

### One divergence from your spec, and why:

My original plan was to use semantic search powered by an LLM to retrieve relevant clothing listings. During implementation I instead used deterministic keyword matching with optional size and price filtering. This approach is faster, easier to debug, and produces consistent results while still satisfying the project requirements. I reserved the language model for the creative tasks of outfit recommendation and Fit Card generation, where it provides the greatest benefit.
