from typing import Any
from transformers import pipeline
from transformers import BertTokenizer, BertForSequenceClassification
import openai
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

    prompt_text = f"""Only preseto query without any other information
    Question: {question}
    {datastore}
    """

    response = openai.chat.completions.create(
        model="gpt-4",  # Adjust based on availability and your requirements
        messages=[{"role": "user", "content": prompt_text}],
    )

    return response.choices[0].message.content
