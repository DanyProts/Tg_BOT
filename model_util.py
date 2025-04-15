import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from tqdm import tqdm

class AttentionPooling(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.attention = nn.Linear(hidden_size, 1)

    def forward(self, token_embeddings, attention_mask):
        scores = self.attention(token_embeddings).squeeze(-1)
        scores = scores.masked_fill(attention_mask == 0, -1e9)
        weights = F.softmax(scores, dim=1).unsqueeze(-1)
        weighted = token_embeddings * weights
        return weighted.sum(dim=1)
def get_embeddings(texts, model, tokenizer, device, pooling):
    encoded = tokenizer(
        texts,
        padding=True,
        truncation=True,
        return_tensors="pt",
        max_length=512
    ).to(device)

    with torch.no_grad():
        output = model(**encoded)
        last_hidden_state = output.last_hidden_state
        attention_mask = encoded["attention_mask"]
        return pooling(last_hidden_state, attention_mask)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "bert-base-multilingual-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).to(device)
pooling = AttentionPooling(model.config.hidden_size).to(device)