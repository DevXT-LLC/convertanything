from enum import Enum
from pydantic import BaseModel
from typing import Type, get_args, get_origin, Union, List
import json
import openai
import uuid
import logging
import os


logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def convertanything(
    input_string: str,
    model: Type[BaseModel],
    server: str = "https://api.openai.com",
    api_key: str = None,
    llm: str = "gpt-3.5-turbo-16k",
    max_failures: int = 3,
    response_type: str = None,
    **kwargs,
):
    input_string = str(input_string)
    openai.base_url = f"{server}/v1/"
    openai.api_key = api_key if api_key else server
    fields = model.__annotations__
    field_descriptions = []
    for field, field_type in fields.items():
        description = f"{field}: {field_type}"
        if get_origin(field_type) == Union:
            field_type = get_args(field_type)[0]
        if isinstance(field_type, type) and issubclass(field_type, Enum):
            enum_values = ", ".join([f"{e.name} = {e.value}" for e in field_type])
            description += f" (Enum values: {enum_values})"
        field_descriptions.append(description)
    schema = "\n".join(field_descriptions)
    prompt = f"""Act as a JSON converter that converts any text into the desired JSON format based on the schema provided. Respond only with JSON in a properly formatted markdown code block, no explanations. Make your best assumptions based on data to try to fill in information to match the schema provided.
    **DO NOT ADD FIELDS TO THE MODEL OR CHANGE TYPES OF FIELDS, FOLLOW THE PYDANTIC SCHEMA!**
    **Reformat the following information into a structured format according to the schema provided:**

## Information:
{input_string}

## Pydantic Schema:
{schema}

JSON Structured Output:
    """
    response = ""
    messages = [{"role": "user", "content": prompt}]
    if "prompt_name" in kwargs:
        messages[0]["prompt_name"] = kwargs["prompt_name"]
        if "prompt_category" not in kwargs:
            messages[0]["prompt_category"] = "Default"
        else:
            messages[0]["prompt_category"] = kwargs["prompt_category"]
    completion = openai.chat.completions.create(
        model=llm,
        messages=messages,
        temperature=0.5,
        max_tokens=4096,
        top_p=0.95,
        stream=False,
        user=str(uuid.uuid4()),
    )
    response = completion.choices[0].message.content
    if "```json" in response:
        response = response.split("```json")[1].split("```")[0].strip()
    elif "```" in response:
        response = response.split("```")[1].strip()
    try:
        response = json.loads(response)
        if response_type == "json":
            return response
        else:
            return model(**response)
    except Exception as e:
        if "failures" in kwargs:
            failures = int(kwargs["failures"]) + 1
            if failures > max_failures:
                logging.error(
                    f"Error: {e} . Failed to convert the response to the model after 3 attempts. Response: {response}"
                )
                return (
                    response
                    if response
                    else "Failed to convert the response to the model."
                )
        else:
            failures = 1
        logging.warning(
            f"Error: {e} . Failed to convert the response to the model, trying again. {failures}/3 failures. Response: {response}"
        )
        return convertanything(
            input_string=input_string,
            model=model,
            server=server,
            api_key=api_key,
            llm=llm,
            max_failures=max_failures,
            failures=failures,
            **kwargs,
        )


def remap_fields(converted_data: dict, data: List[dict]) -> List[dict]:
    mapped_list = []
    for info in data:
        new_data = {}
        for key, value in converted_data.items():
            item = [k for k, v in data[0].items() if v == value]
            if item:
                new_data[key] = info[item[0]]
        mapped_list.append(new_data)
    return mapped_list


def convert_list_of_dicts(
    data: List[dict],
    model: Type[BaseModel],
    server="https://api.openai.com",
    api_key=None,
    llm="gpt-3.5-turbo-16k",
    **kwargs,
):
    converted_data = convertanything(
        input_string=json.dumps(data[0]),
        model=model,
        server=server,
        api_key=api_key,
        llm=llm,
        **kwargs,
    )
    mapped_list = remap_fields(converted_data=converted_data.model_dump(), data=data)
    return mapped_list
