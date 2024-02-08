# convertanything

`convertanything` is a simple way to convert any unstructured texts into pydantic models in Python with the use of language models. See the [examples notebook](examples.ipynb) for more details.

## Installation

```bash
pip install convertanything
```

## Usage

```python
from convertanything import convertanything
from pydantic import BaseModel
from typing import List

class Person(BaseModel):
    name: str
    age: int
    email: str
    interests: List[str]

response = convertanything(
    input_string="Hi my name is John Doe, I am 30 years old, my email is johndoe@example.com . I like to go fishing.",
    model=Person,
    api_key="Your OpenAI API Key",
)
print(response)
```
