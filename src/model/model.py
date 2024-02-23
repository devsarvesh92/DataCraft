from transformers import pipeline
from transformers import BertTokenizer, BertForSequenceClassification

# Load the model
model = BertForSequenceClassification.from_pretrained("my_model_directory")
tokenizer = BertTokenizer.from_pretrained("my_model_directory")

# Initialize the pipeline
classify = pipeline("text-classification", model=model, tokenizer=tokenizer)

# Predict
query = "total revenue last year"
predictions = classify(query)

# data source

# Query builder
# total revenue last year -> sales {}



# predicted_label = id_to_label[predictions[0]['label'].split('_')[-1]]

print(f"Predicted data source: {predictions}")
