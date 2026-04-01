# Python Syntax Guide for Beginners

A line-by-line walkthrough of every Python concept used in `main.py`.

---

## 1. Imports

```python
import asyncio
from dataclasses import dataclass
from typing import Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
```

### What is an import?

An **import** brings code from another module (file/library) into your script so you can use it.

| Syntax | Meaning |
|---|---|
| `import asyncio` | Import the entire `asyncio` module. You call things as `asyncio.run(...)`. |
| `from dataclasses import dataclass` | Import only `dataclass` from the `dataclasses` module. You use `dataclass` directly without a prefix. |

### Modules used here

- **`asyncio`** -- Built-in module for writing asynchronous (non-blocking) code.
- **`dataclasses`** -- Built-in module that provides `@dataclass`, a shortcut for creating classes that mainly hold data.
- **`typing`** -- Built-in module for type hints. `Any` means "any type at all."
- **`dotenv`** -- Third-party library. `load_dotenv()` reads a `.env` file and loads its key-value pairs into environment variables.
- **`pydantic`** -- Third-party library for data validation. `BaseModel` and `Field` let you define validated data structures.
- **`pydantic_ai`** -- Third-party library that connects Pydantic models with AI agents. `Agent` and `RunContext` are its core classes.

---

## 2. Calling a Function

```python
load_dotenv()
```

This calls the `load_dotenv` function with no arguments. The parentheses `()` are what actually **execute** the function. Without them, you'd just be referencing the function object, not running it.

---

## 3. Decorators

```python
@dataclass
class Patient:
    ...
```

A **decorator** is the `@something` line placed directly above a class or function. It modifies or enhances the thing below it.

`@dataclass` automatically generates several special methods for the class:
- `__init__` -- so you can write `Patient(id=1, first_name="John", ...)`
- `__repr__` -- so printing a `Patient` shows a readable string
- `__eq__` -- so you can compare two `Patient` objects with `==`

Without `@dataclass`, you'd have to write all of that yourself:

```python
# Without @dataclass -- you'd need all of this manually:
class Patient:
    def __init__(self, id, first_name, last_name, age, vitals):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.vitals = vitals
```

---

## 4. Type Hints (Type Annotations)

```python
id: int
first_name: str
last_name: str
age: int
vitals: dict[str, Any]
```

Type hints tell readers (and tools) what type of value a variable should hold. Python does **not** enforce these at runtime -- they are documentation and are used by type checkers like `mypy`.

| Hint | Meaning |
|---|---|
| `int` | An integer (whole number) like `1`, `42`, `-3` |
| `str` | A string (text) like `"John"` |
| `dict[str, Any]` | A dictionary whose **keys** are strings and **values** can be anything |
| `Any` | Literally any type -- no restriction |

### Generic types

`dict[str, Any]` is a **generic type**. The square brackets `[]` parameterize the type:

```python
dict[str, Any]     # keys are str, values are Any
list[int]          # a list of integers
tuple[str, int]    # a tuple with a string and an integer
```

---

## 5. Classes

```python
class DatabaseConn:
    def __init__(self, db: dict[int, Patient]):
        self._db = db
```

### What is a class?

A **class** is a blueprint for creating objects. Objects bundle data (attributes) and behavior (methods) together.

### `__init__` -- The Constructor

`__init__` is a **special method** (also called a "dunder" method because of the double underscores). It runs automatically when you create a new instance:

```python
conn = DatabaseConn(Patient_DB)  # This calls __init__ with db=Patient_DB
```

### `self`

`self` refers to the **current instance** of the class. Every method in a class receives `self` as its first parameter. When you write `self._db = db`, you're storing `db` as an attribute on that specific object.

### Underscore prefix `_db`

A single leading underscore (`_db`) is a **convention** meaning "this is intended to be private -- don't access it directly from outside the class." Python doesn't enforce this; it's a hint to other programmers.

---

## 6. Methods and Return Types

```python
def get_patient_name(self, patient_id: int) -> str:
    patient = self._db[patient_id]
    return f"{patient.first_name} {patient.last_name}"
```

### `def` -- Function/Method Definition

`def` defines a function. Inside a class, functions are called **methods**.

### `-> str` -- Return Type Hint

The arrow `->` followed by a type tells readers what the function returns. Here, `-> str` means "this method returns a string."

### Dictionary Access `self._db[patient_id]`

Square brackets on a dictionary look up a value by its key:

```python
my_dict = {1: "apple", 2: "banana"}
my_dict[1]   # Returns "apple"
my_dict[2]   # Returns "banana"
```

### f-strings (Formatted String Literals)

```python
f"{patient.first_name} {patient.last_name}"
```

An **f-string** starts with `f"` and lets you embed expressions inside `{}`. Python evaluates the expression and inserts the result into the string:

```python
name = "Alice"
age = 30
f"My name is {name} and I am {age} years old."
# Result: "My name is Alice and I am 30 years old."
```

---

## 7. Dictionaries

```python
Patient_DB = {
    1: Patient(id=1, first_name="John", last_name="Doe", age=18,
               vitals={"heart_rate": 72, "blood_pressure": "30/80", "blood_sugar": "100/80"}),
    2: Patient(id=2, first_name="Jane", last_name="Smith", age=45,
               vitals={"heart_rate": 88, "blood_pressure": "160/100", "blood_sugar": "95/80"}),
    3: Patient(...),
}
```

A **dictionary** (`dict`) maps **keys** to **values** using the syntax `{key: value}`.

Here:
- Keys are integers (`1`, `2`, `3`) -- the patient IDs.
- Values are `Patient` objects created by calling `Patient(...)`.

### Nested dictionaries

The `vitals` parameter is itself a dictionary:

```python
{"heart_rate": 72, "blood_pressure": "30/80"}
```

Keys are strings, values are a mix of integers and strings (hence the `dict[str, Any]` type hint).

---

## 8. Keyword Arguments

```python
Patient(id=1, first_name="John", last_name="Doe", age=18, vitals={...})
```

When calling a function or constructor, you can pass arguments **by name** using `name=value` syntax. This is called a **keyword argument**. Benefits:

- Order doesn't matter (you could write `age=18, id=1` and it would still work).
- The code is self-documenting -- you can see what each value means.

---

## 9. Instantiation (Creating Objects)

```python
conn = DatabaseConn(Patient_DB)
```

This creates a new **instance** of the `DatabaseConn` class:

1. Python creates a new, empty `DatabaseConn` object.
2. Python calls `DatabaseConn.__init__(self, db=Patient_DB)`.
3. The `__init__` method stores `Patient_DB` as `self._db`.
4. The new object is assigned to the variable `conn`.

---

## 10. Class Inheritance (via Pydantic)

```python
class Triageoutput(BaseModel):
    response_text: str = Field(description="Triage recommendation for the patient.")
    triage_level: str = Field(description="Triage level for the patient.")
    escalate: bool = Field(description="Escalate for the human nurse.")
```

### Inheritance `(BaseModel)`

The parentheses after a class name mean "this class **inherits from** (extends) `BaseModel`." `Triageoutput` gets all the behavior of `BaseModel` plus anything you define.

### `bool` type

`bool` stands for **boolean** -- a value that is either `True` or `False`.

### `Field(description=...)`

`Field(...)` sets metadata and validation rules for each attribute. Here it only sets a `description`, which documents the field and is passed to the AI model so it knows what each field means.

---

## 11. Multi-line Strings (Parenthesized)

```python
system_prompt=(
    "You are a medical triage assistant. Given a patient's name and vitals, "
    "assess their condition and provide a triage recommendation. "
    "Assign a triage level (e.g. immediate, urgent, less urgent, non-urgent) "
    "and determine whether to escalate to a human nurse."
),
```

Python automatically concatenates adjacent string literals. Wrapping them in parentheses `()` lets you split a long string across multiple lines without using `+` or `\n`. The result is a single string.

---

## 12. Decorator with Method Reference

```python
@triage_agent.tool
def get_patient_info(ctx: RunContext[TriageDependencies]) -> dict[str, Any]:
```

`@triage_agent.tool` is a decorator that **registers** this function as a tool the AI agent can call. It's the same decorator concept as `@dataclass`, but here the decorator is a method on the `triage_agent` object rather than a standalone function.

### Docstrings

```python
"""Fetch the patient's name and latest vitals from the database."""
```

A **docstring** is a string literal placed as the first statement inside a function or class. It documents what the function does. The AI agent reads this docstring to understand when and how to use the tool.

### `RunContext[TriageDependencies]`

This is a **generic type**. `RunContext` is a class that can be parameterized with a type. `RunContext[TriageDependencies]` means "a RunContext that carries `TriageDependencies` as its dependency data." Inside the function, `ctx.deps` gives you access to the `TriageDependencies` instance.

---

## 13. Dot Notation (Attribute Access)

```python
ctx.deps.db.get_patient_name(ctx.deps.patient_id)
```

The dot `.` accesses an **attribute** or **method** on an object. Reading this left to right:

1. `ctx` -- the RunContext object
2. `ctx.deps` -- the dependencies object (`TriageDependencies`) stored inside ctx
3. `ctx.deps.db` -- the `DatabaseConn` stored inside the dependencies
4. `ctx.deps.db.get_patient_name(...)` -- call the `get_patient_name` method on that DatabaseConn

---

## 14. Async / Await

```python
async def main():
    for patient_id in Patient_DB:
        deps = TriageDependencies(patient_id=patient_id, db=conn)
        result = await triage_agent.run(
            "Fetch the patient info and include their name and vitals in your recommendation.", deps=deps
        )
```

### `async def`

Defines an **asynchronous function** (a coroutine). Async functions can pause execution while waiting for slow operations (like API calls) without blocking the entire program.

### `await`

`await` pauses the current function until the awaited operation completes. Here, `triage_agent.run(...)` makes an API call to Claude. While waiting for the response, Python could (in theory) do other work.

### Why async?

The AI agent calls an external API over the network. Without async, the program would sit idle during each API call. With async, the program structure supports concurrent operations (though in this simple loop, calls happen one at a time).

---

## 15. For Loops

```python
for patient_id in Patient_DB:
```

A `for` loop iterates over an **iterable**. When you iterate over a dictionary, you get its **keys**:

```python
my_dict = {1: "a", 2: "b", 3: "c"}
for key in my_dict:
    print(key)
# Prints: 1, 2, 3
```

So `patient_id` takes the values `1`, `2`, `3` on successive iterations.

---

## 16. Accessing Results

```python
result.output.response_text
result.output.triage_level
result.output.escalate
```

`result` is the object returned by `triage_agent.run(...)`. The `.output` attribute contains the structured `Triageoutput` object, and you access its fields with dot notation.

---

## 17. The `if __name__ == "__main__":` Guard

```python
if __name__ == "__main__":
    asyncio.run(main())
```

### What does this do?

Every Python file has a special variable called `__name__`:
- If the file is **run directly** (`python main.py`), `__name__` is set to `"__main__"`.
- If the file is **imported** by another file, `__name__` is set to the module name (e.g., `"main"`).

This guard ensures the code inside only runs when you execute the file directly, not when it's imported as a module.

### `asyncio.run(main())`

`asyncio.run()` is the entry point for running an async function from synchronous code. It:
1. Creates a new event loop.
2. Runs the `main()` coroutine until it completes.
3. Cleans up the event loop.

---

## Quick Reference Table

| Syntax | Name | Example |
|---|---|---|
| `import X` | Module import | `import asyncio` |
| `from X import Y` | Selective import | `from typing import Any` |
| `@decorator` | Decorator | `@dataclass` |
| `x: int` | Type hint | `age: int` |
| `def f(self)` | Method definition | `def get_patient_name(self, ...)` |
| `-> str` | Return type hint | `def func() -> str:` |
| `f"...{expr}..."` | f-string | `f"Hello {name}"` |
| `{k: v}` | Dictionary literal | `{1: Patient(...)}` |
| `obj.attr` | Attribute access | `ctx.deps.db` |
| `class A(B):` | Inheritance | `class Triageoutput(BaseModel):` |
| `async def` | Async function | `async def main():` |
| `await` | Await coroutine | `await triage_agent.run(...)` |
| `for x in y:` | For loop | `for patient_id in Patient_DB:` |
| `X[Y]` | Generic type / subscript | `dict[str, Any]` |