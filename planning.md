# FitFindr — planning.md

> Complete this document before writing any implementation code.

---

# Tools

## Tool 1: search_listings

**What it does:**
Searches the clothing listings database using the user's preferences such as clothing description, size, and budget. Returns the best matching items sorted by relevance.

**Input parameters:**

- `description` (str): Keywords describing the clothing item the user wants.
- `size` (str): User's clothing size.
- `max_price` (float): Maximum amount the user wants to spend.

**What it returns:**
A list of matching clothing listings. Each listing contains:

- item name
- category
- brand
- size
- price
- color
- image URL (if available)
- listing ID

**What happens if it fails or returns nothing:**
The agent informs the user that no matching items were found and suggests broadening the search by increasing the budget or changing the description.

---

## Tool 2: suggest_outfit

**What it does:**
Builds a complete outfit using the selected clothing item and the user's wardrobe. It tries to create a coordinated outfit based on color, clothing type, and style.

**Input parameters:**

- `new_item` (dict): The clothing item selected from search results.
- `wardrobe` (dict): The user's saved wardrobe items.

**What it returns:**
An outfit recommendation containing:

- top
- bottom
- shoes
- accessories (optional)
- styling explanation

**What happens if it fails or returns nothing:**
If the wardrobe is empty, the agent styles the new item using general fashion recommendations instead of wardrobe items.

---

## Tool 3: create_fit_card

**What it does:**
Creates the final outfit summary ("Fit Card") that presents the recommended clothing combination in an easy-to-read format.

**Input parameters:**

- `outfit` (str): Description of the completed outfit.
- `new_item` (dict): The clothing item the user searched for.

**What it returns:**
A formatted Fit Card containing:

- featured clothing item
- complete outfit
- styling notes
- estimated total cost (if applicable)

**What happens if it fails or returns nothing:**
The agent displays the selected clothing item with a note that a complete outfit could not be generated.

---

# Planning Loop

**How does your agent decide which tool to call next?**

1. Receive the user's clothing request.
2. Call `search_listings()` to find matching items.
3. If no listings are found, stop and return suggestions for modifying the search.
4. Otherwise, allow one matching item to become the selected item.
5. Call `suggest_outfit()` using the selected item and the user's wardrobe.
6. Store the generated outfit.
7. Call `create_fit_card()` to build the final response.
8. Return the completed Fit Card to the user.

The planning loop ends after either:

- no search results are found, or
- the Fit Card has been successfully created.

---

# State Management

The agent stores session information in memory during the interaction.

Tracked state includes:

- original user query
- search parameters
- search results
- selected clothing item
- user's wardrobe
- generated outfit
- final Fit Card

Each tool receives the output from the previous tool. For example:

User Query
→ Search Results
→ Selected Item
→ Outfit Recommendation
→ Fit Card

No information needs to persist between separate user sessions.

---

# Error Handling

| Tool            | Failure mode                          | Agent response                                                                                              |
| --------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| search_listings | No results match the query            | Inform the user and recommend changing the description, size, or budget.                                    |
| suggest_outfit  | Wardrobe is empty                     | Create an outfit using common styling recommendations instead of wardrobe items.                            |
| create_fit_card | Outfit input is missing or incomplete | Display the selected clothing item with styling notes explaining that a full outfit could not be generated. |

---

# Architecture

```text
                +----------------+
                |     User       |
                +--------+-------+
                         |
                         v
               +-------------------+
               |   Planning Loop   |
               +---------+---------+
                         |
                         v
             +----------------------+
             | search_listings()    |
             +----------+-----------+
                        |
          No Results <--+--> Listings Found
              |                 |
              |                 v
              |      Store Selected Item
              |                 |
              |                 v
              |     +----------------------+
              |     | suggest_outfit()     |
              |     +----------+-----------+
              |                |
              |      Wardrobe Empty?
              |          /         \
              |        Yes          No
              |         |            |
              |         v            v
              |  Generic Styling  Outfit Created
              |          \          /
              |           \        /
              |            v      v
              |      +----------------------+
              |      | create_fit_card()    |
              |      +----------+-----------+
              |                 |
              +-----------------+
                        |
                        v
                Final Response

        Shared Session State
        ---------------------
        • User query
        • Search filters
        • Search results
        • Selected item
        • Wardrobe
        • Outfit
        • Fit Card
```

---

# AI Tool Plan

### Milestone 3 — Individual tool implementations

**Tool:** ChatGPT

**Input:**
The specification for each tool from this planning document.

**Expected output:**
Python implementations for:

- `search_listings()`
- `suggest_outfit()`
- `create_fit_card()`

**Verification:**

- Test searches with multiple clothing descriptions.
- Verify budget filtering.
- Verify outfit generation with both populated and empty wardrobes.
- Verify Fit Card formatting.

---

### Milestone 4 — Planning loop and state management

**Tool:** ChatGPT

**Input:**
Planning Loop, State Management, and Architecture sections.

**Expected output:**
A controller function that:

- calls tools in the proper order
- maintains session state
- handles failures gracefully

**Verification:**
Run several end-to-end user queries and confirm:

- correct tool order
- state updates correctly
- proper handling of empty search results and empty wardrobes

---

# A Complete Interaction (Step by Step)

**Example user query:**

> "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

### Step 1:

The agent calls:

`search_listings(description="vintage graphic tee", size="M", max_price=30)`

Returns three matching shirts.

---

### Step 2:

The highest-ranked shirt is selected.

The agent calls:

`suggest_outfit(new_item=selected_shirt, wardrobe=user_wardrobe)`

Returns:

- graphic tee
- baggy jeans
- chunky sneakers
- silver chain
- styling explanation

---

### Step 3:

The outfit is passed into:

`create_fit_card(outfit, selected_shirt)`

Returns a formatted Fit Card.

---

### Final output to user:

```
Recommended Item
Vintage Nike Graphic Tee
$24.99

Suggested Outfit
• Vintage Nike Graphic Tee
• Black Baggy Jeans
• White Chunky Sneakers
• Silver Chain

Style Notes
This outfit has a relaxed streetwear aesthetic. The oversized tee pairs well with loose-fitting jeans and chunky sneakers for a balanced vintage look.

Estimated Total Cost
$24.99 (new item only)
```
