from transformers import pipeline
from transformers import BertTokenizer, BertForSequenceClassification

def get_datasource(query:str):
    # Load the model
    model = BertForSequenceClassification.from_pretrained("data_craft_model")
    tokenizer = BertTokenizer.from_pretrained("data_craft_model")

    # Initialize the pipeline
    classify = pipeline("text-classification", model=model, tokenizer=tokenizer)

    # Predict
    predictions = classify(query)


    label_mapping = {
        "LABEL_0": "transactions, accounts",
        "LABEL_1": "payments, accounts"
    }

    return label_mapping[predictions[0]['label']]
