import os
import torch
import json
import random
from tqdm import trange, tqdm
from transformers import BertTokenizer, BertForMaskedLM


# 这里尝试了许多版本的bert模型，ernie-1.0的效果最好
model_checkpoint = '/data/immortal/pretrained_model/ernie-1.0/'
tokenizer = BertTokenizer.from_pretrained(model_checkpoint)
model = BertForMaskedLM.from_pretrained(model_checkpoint)


def BERT_for_mask_fill(text, ratio=0.1):
    tokens = tokenizer.tokenize(text)
    tokens = tokens[:510]
    select_index = random.sample(range(len(tokens)), int(len(tokens)*ratio))
    if select_index == []:
        return text
    select_index = sorted(select_index)
    for i, token in enumerate(tokens):
        if i in select_index:
            tokens[i] = '[MASK]'
    input_ids = torch.tensor([tokenizer.convert_tokens_to_ids(["[CLS]"] + tokens + ["[SEP]"])], dtype=torch.long)
    with torch.no_grad():
        logits = model(input_ids).logits
    mask_token_index = (input_ids == tokenizer.mask_token_id)[0].nonzero(as_tuple=True)[0]
    predicted_token_id = logits[0, mask_token_index].argmax(axis=-1)
    predict_tokens = []
    for i in range(len(predicted_token_id)):
        predict_tokens.append(tokenizer.decode(predicted_token_id[i:i+1]))
    augment_tokens = tokens[:]
    for i, index_ in enumerate(select_index):
        augment_tokens[index_] = predict_tokens[i]
    return ''.join(augment_tokens).replace('##', '')


if __name__ == '__main__':
  text = ''
  aug_text = BERT_for_mask_fill(text, ratio=0.1)
