import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import BertTokenizer
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
import torch

# Load the dataset
df = pd.read_csv("src/train/training_data_balanced.csv")

# Split the dataset
train_texts, val_texts, train_labels, val_labels = train_test_split(df['query'].tolist(), df['label'].tolist(), test_size=.3)

# Initialize the tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

label_dict = {
    "transactions, accounts": 0,
    "payments, accounts": 1
}


# Tokenize the text
train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128)
val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=128)

# Convert to torch tensors
train_seq = torch.tensor(train_encodings['input_ids'])
train_mask = torch.tensor(train_encodings['attention_mask'])
train_y = torch.tensor([label_dict[label] for label in train_labels])  # Ensure label_dict maps labels to integers

val_seq = torch.tensor(val_encodings['input_ids'])
val_mask = torch.tensor(val_encodings['attention_mask'])
val_y = torch.tensor([label_dict[label] for label in val_labels])

# Create DataLoaders
batch_size = 32
train_data = TensorDataset(train_seq, train_mask, train_y)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)

val_data = TensorDataset(val_seq, val_mask, val_y)
val_sampler = SequentialSampler(val_data)
val_dataloader = DataLoader(val_data, sampler=val_sampler, batch_size=batch_size)

from transformers import BertForSequenceClassification

# Load the BERT model
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=len(label_dict))

# Specify the device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


from transformers import AdamW, get_linear_schedule_with_warmup
from tqdm import tqdm

# Optimizer and scheduler
optimizer = AdamW(model.parameters(), lr=2e-5, correct_bias=False)
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=len(train_dataloader) * 10)

# Training loop
epochs = 10
for epoch in range(epochs):
    model.train()
    total_loss = 0
    for batch in tqdm(train_dataloader):
        batch = [r.to(device) for r in batch]
        inputs = {'input_ids': batch[0], 'attention_mask': batch[1], 'labels': batch[2]}
        model.zero_grad()
        outputs = model(**inputs)
        loss = outputs[0]
        total_loss += loss.item()
        loss.backward()
        optimizer.step()
        scheduler.step()
    print(f"Epoch {epoch}, Loss: {total_loss / len(train_dataloader)}")

    # Validation step...
model.save_pretrained("./data_craft_model")
tokenizer.save_pretrained("./data_craft_model")

