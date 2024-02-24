from typing import Any
from transformers import pipeline
from transformers import BertTokenizer, BertForSequenceClassification
import openai

openai.api_key = 'TO-BE-ADDED'

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
    hint: 
    Tenant ID Clarity: Ensure that the API call does not lead to ambiguity regarding the tenant ID. This means explicitly specifying the tenant ID in a manner that prevents confusion or errors related to tenant identification.
    Use of extract Function for Monthly Aggregation: If the request involves aggregation based on the month, incorporate the extract function to accurately extract the month from date fields. This is crucial for performing precise monthly aggregation tasks.
    Consistent Use of extract in SELECT and GROUP BY: In cases where the extract function is used in the SELECT clause for extracting specific date parts (like month), it is essential to also use extract in the GROUP BY clause. This ensures that the data aggregation aligns with the selected date part and maintains consistency in the query's logic.
    If there is a check word for payments use it as a type
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




