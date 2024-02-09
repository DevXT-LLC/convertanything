from pydantic import BaseModel
from typing import Type
import json
import openai


def convertanything(
    input_string: str,
    model: Type[BaseModel],
    api_key=None,
    server="https://api.openai.com",
    llm="gpt-3.5-turbo-16k",
):
    if not isinstance(input_string, str):
        input_string = str(input_string)
    openai.base_url = f"{server}/v1/"
    openai.api_key = api_key if api_key else server
    fields = model.model_fields
    field_descriptions = [f"{field}: {fields[field]}" for field in fields]
    schema = "\n".join(field_descriptions)
    system_message = "Act as a JSON converter that converts any text into the desired JSON format based on the schema provided. Respond only with JSON in a properly formatted markdown code block, no explanations."
    if not llm.startswith("gpt"):
        system_message += " After the request is fulfilled, end with </s>."
    prompt = f"""
**Reformat the following information into a structured format according to the schema provided:**

## Information:
{input_string}

## Schema:
{schema}

JSON Structured Output:
    """
    response = ""
    if llm.startswith("gpt"):
        prompt = f"{system_message}\n{prompt}"
    completion = openai.chat.completions.create(
        model=llm,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024,
        top_p=0.95,
        stream=False,
        extra_body={
            "system_message": system_message,
        },
    )
    response = completion.messages[1]["content"]
    response = str(response).split("```json")[1].split("```")[0].strip()
    try:
        response = json.loads(response)
        return model(**response)
    except:
        print(response)
        print("Failed to convert the response to the model, trying again.")
        return convertanything(input_string=input_string, model=model)
