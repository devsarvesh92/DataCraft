from typing import Any
from transformers import pipeline
from transformers import BertTokenizer, BertForSequenceClassification
import openai
import re

openai.api_key = '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'

def get_datasource(query: str):
    # Load the model
    model = BertForSequenceClassification.from_pretrained("data_craft_model")
    tokenizer = BertTokenizer.from_pretrained("data_craft_model")

    # Initialize the pipeline
    classify = pipeline("text-classification", model=model, tokenizer=tokenizer)

    # Predict
    predictions = classify(query)

    label_mapping = {
        "LABEL_0": "transactions, accounts",
        "LABEL_1": "payments, accounts",
    }

    return label_mapping[predictions[0]["label"]]


def get_query(question: str, datastore: dict[str, Any]):

    prompt_text = f"""Presto query for: Question: {question}
    {datastore}
    """

    response = openai.chat.completions.create(
        model="gpt-4",  # Adjust based on availability and your requirements
        messages=[{"role": "user", "content": prompt_text}],
    )
    result =  response.choices[0].message.content

    parts = result.lower().split("```")

    if len(parts) > 1:
        query = parts[1].replace("\n", " ").replace("sql", " ")
    else:
        # for simple queries
        query = parts[0].replace("\n", " ").replace("sql", " ")
    return query




