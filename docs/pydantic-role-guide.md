# The Role of Pydantic in This Project

This document explains what Pydantic is and how it is used in the Health Triage application.

---

## What is Pydantic?

Pydantic is a Python library for **data validation and serialization**. You define the shape of your data using Python classes, and Pydantic automatically:

- **Validates** that incoming data matches the expected types.
- **Converts** data to the correct types when possible (e.g., the string `"42"` becomes the integer `42`).
- **Raises clear errors** when data is invalid.

This project uses two Pydantic-related packages:

| Package | Purpose |
|---|---|
| `pydantic` | Core library for defining validated data models |
| `pydantic-ai` | Extension that connects Pydantic models with AI agents (Claude, OpenAI, etc.) |

---

## How Pydantic Is Used in This Project

### 1. Structured AI Output with `BaseModel`

The most important use of Pydantic here is defining the **exact structure** the AI agent must return.

```python
from pydantic import BaseModel, Field

class Triageoutput(BaseModel):
    response_text: str = Field(description="Triage recommendation for the patient.")
    triage_level: str = Field(description="Triage level for the patient.")
    escalate: bool = Field(description="Escalate for the human nurse.")
```

#### What `BaseModel` gives us

Without Pydantic, the AI would return free-form text and you'd have to parse it yourself -- guessing where the triage level is, whether "yes" means `True`, etc. With Pydantic:

1. **The AI knows the expected format.** The field names, types, and descriptions are passed to the AI model as part of its instructions. It knows it must return JSON matching this exact schema.

2. **The response is validated automatically.** When the AI responds, Pydantic checks:
   - Is `response_text` actually a string?
   - Is `triage_level` actually a string?
   - Is `escalate` actually a boolean (`true`/`false`)?

   If anything is wrong, Pydantic raises a validation error instead of letting bad data through.

3. **You get a typed Python object.** Instead of parsing a raw string or dictionary, you access clean attributes:
   ```python
   result.output.response_text   # str
   result.output.triage_level    # str
   result.output.escalate        # bool
   ```

#### What `Field(description=...)` does

`Field` adds metadata to each attribute. The `description` parameter is particularly important in AI applications because:

- It is included in the **JSON schema** sent to the AI model.
- The AI reads these descriptions to understand what each field should contain.
- Better descriptions lead to better, more consistent AI outputs.

Think of it as instructions to the AI for each field:

```python
escalate: bool = Field(description="Escalate for the human nurse.")
# Tells the AI: "This field should be True if a human nurse needs to be involved,
#                False otherwise."
```

---

### 2. Agent Configuration with `pydantic-ai`

The `pydantic-ai` library builds on Pydantic to create AI agents that accept typed inputs and return typed outputs.

```python
from pydantic_ai import Agent, RunContext

triage_agent = Agent(
    "anthropic:claude-sonnet-4-5",
    deps_type=TriageDependencies,
    output_type=Triageoutput,
    system_prompt="You are a medical triage assistant..."
)
```

#### `output_type=Triageoutput`

This tells the agent: "When you respond, your output **must** conform to the `Triageoutput` schema." Behind the scenes, `pydantic-ai`:

1. Converts the `Triageoutput` Pydantic model into a **JSON schema**.
2. Sends that schema to Claude as part of the prompt.
3. Parses Claude's response and validates it against the schema.
4. Returns a typed `Triageoutput` object you can use in Python.

This is the core value proposition: **the AI's unstructured text response becomes a validated, structured Python object.**

#### `deps_type=TriageDependencies`

This tells the agent what type of **dependency data** it will receive at runtime. While `TriageDependencies` is a plain dataclass (not a Pydantic model), `pydantic-ai` uses this type information to ensure type safety when tools access dependencies.

---

### 3. Type-Safe Tool Context with `RunContext`

```python
@triage_agent.tool
def get_patient_info(ctx: RunContext[TriageDependencies]) -> dict[str, Any]:
    """Fetch the patient's name and latest vitals from the database."""
    name = ctx.deps.db.get_patient_name(ctx.deps.patient_id)
    vitals = ctx.deps.db.get_latest_vitals(ctx.deps.patient_id)
    return {"name": name, "vitals": vitals}
```

`RunContext[TriageDependencies]` is a **generic type** from `pydantic-ai`. It wraps the dependency object and makes it available to the tool function via `ctx.deps`.

The flow:

1. You run the agent with specific dependencies:
   ```python
   deps = TriageDependencies(patient_id=1, db=conn)
   result = await triage_agent.run("...", deps=deps)
   ```

2. The AI decides to call the `get_patient_info` tool.

3. `pydantic-ai` invokes the tool function, passing a `RunContext` that contains the `deps` you provided.

4. The tool accesses `ctx.deps.patient_id` and `ctx.deps.db` to fetch data from the database.

5. The tool's return value (`dict`) is sent back to the AI, which uses it to formulate its final `Triageoutput`.

---

## The Complete Data Flow

Here is how Pydantic ties everything together in a single agent run:

```
You call triage_agent.run(prompt, deps=TriageDependencies(...))
    |
    v
pydantic-ai sends the prompt + Triageoutput JSON schema to Claude
    |
    v
Claude decides it needs patient data --> calls get_patient_info tool
    |
    v
pydantic-ai invokes get_patient_info(ctx: RunContext[TriageDependencies])
    |
    v
Tool fetches data from DatabaseConn and returns a dict
    |
    v
pydantic-ai sends the tool result back to Claude
    |
    v
Claude generates a JSON response matching the Triageoutput schema
    |
    v
pydantic-ai validates the JSON with Pydantic
    |
    v
You receive result.output as a validated Triageoutput object
    - result.output.response_text  --> str
    - result.output.triage_level   --> str
    - result.output.escalate       --> bool
```

---

## Pydantic vs Dataclasses in This Project

The project uses **both** Pydantic models and Python dataclasses. Here's why:

| Class | Type | Why |
|---|---|---|
| `Patient` | `@dataclass` | Simple data container. No validation needed -- data is hardcoded in the script. |
| `TriageDependencies` | `@dataclass` | Simple container for passing context to the agent. No AI interaction. |
| `Triageoutput` | `BaseModel` (Pydantic) | **Must** be a Pydantic model because it defines the AI's output schema. Pydantic generates the JSON schema that tells the AI what to return and validates the response. |

**Rule of thumb:** Use Pydantic `BaseModel` when data crosses a trust boundary (user input, API responses, AI output). Use plain dataclasses for internal data that you control.

---

## What Would Happen Without Pydantic?

Without Pydantic, you'd need to:

1. **Manually write prompt instructions** telling the AI to return JSON in a specific format.
2. **Parse the raw text response** (hoping the AI returned valid JSON).
3. **Manually validate every field** -- check types, handle missing fields, convert strings to booleans, etc.
4. **Handle malformed responses** with custom error logic.

With Pydantic, all of this is handled automatically. You define the schema once, and the library takes care of prompt engineering (for the schema), parsing, validation, and type conversion.

---

## Key Pydantic Concepts Summary

| Concept | What It Does | Where It's Used |
|---|---|---|
| `BaseModel` | Base class for validated data models | `Triageoutput` |
| `Field(description=...)` | Adds metadata/descriptions to fields | All fields in `Triageoutput` |
| JSON Schema generation | Converts model to JSON schema for the AI | Automatically by `pydantic-ai` |
| Response validation | Checks AI output matches the schema | Automatically by `pydantic-ai` |
| `RunContext[T]` | Type-safe dependency injection for tools | `get_patient_info` function |
| `Agent(output_type=...)` | Binds a Pydantic model as the agent's output format | `triage_agent` definition |