# convertanything

`convertanything` is a simple way to convert any unstructured texts into pydantic models in Python with the use of language models. See the [examples notebook](https://github.com/DevXT-LLC/convertanything/blob/main/example.ipynb) for more details.

## Installation

```bash
pip install convertanything
```

## Usage Examples

### ezLocalai

To use with [ezLocalai](https://github.com/DevXT-LLC/ezlocalai) in Python, make sure your ezLocalai server is running then run the following code:

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
    input_string="Hi my name is John Doe, I am 30 years old, my email is johndoe@example.com . I like to go fishing and watching football.",
    model=Person,
    api_key="Your ezlocalai API Key",
    server="http://localhost:8091",
)
print(response)
```

### AGiXT

To use with [AGiXT](https://github.com/Josh-XT/AGiXT) in Python, make sure your AGiXT server is running then run the following code:

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
    input_string="Hi my name is John Doe, I am 30 years old, my email is johndoe@example.com . I like to go fishing and watching football.",
    model=Person,
    api_key="Your AGiXT API Key",
    server="http://localhost:7437",
    llm="Your AGiXT Agent Name",
    prompt_name="User Input",
)
print(response)
```

### OpenAI

If you have an OpenAI API key, you can use it as follows with OpenAI language models:

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
    llm="gpt-3.5-turbo",
)
print(response)
```
