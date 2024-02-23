from transformers import BertTokenizer
import pandas as pd
from transformers import BertForSequenceClassification

from torch.utils.data import DataLoader, TensorDataset
from transformers import AdamW

from sklearn.preprocessing import LabelEncoder
import torch


# Load your dataset
df = pd.read_csv("src/train/training_data_min.csv")

# Initialize the tokenizerb
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Tokenize and encode sequences in the dataset
tokens = tokenizer(
    df["query"].tolist(), padding=True, truncation=True, return_tensors="pt"
)

label_encoder = LabelEncoder()
df['encoded_data_source'] = label_encoder.fit_transform(df['data_source'])
labels = torch.tensor(df['encoded_data_source'].values)


dataset = TensorDataset(tokens['input_ids'], tokens['attention_mask'], labels)
batch_size = 100
train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)


num_labels = len(df['data_source'].unique())  # Adjust based on your dataset
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=num_labels)

# Initialize optimizer
optimizer = AdamW(model.parameters(), lr=5e-5)

for epoch in range(4):  # Loop over the dataset multiple times
    for batch in train_loader:
        # Zero the parameter gradients
        optimizer.zero_grad()

        # Forward + backward + optimize
        outputs = model(batch[0], attention_mask=batch[1], labels=batch[2])
        loss = outputs.loss
        loss.backward()
        optimizer.step()

print("Finished Training")


model.save_pretrained("data_craft_model")
tokenizer.save_pretrained("data_craft_model")
