import tensorflow as tf
from matplotlib import pyplot as plt
import pandas as pd
import torch
from transformers import DistilBertModel, DistilBertTokenizer
from torch import cuda

device = 'cuda' if cuda.is_available() else 'cpu'
print(device)

def get_gradient_for_single_question(question, trained_model, corresponding_tokenizer):
    temp_model = DistilBertModel.from_pretrained("distilbert-base-uncased")
    embedding_matrix = temp_model.embeddings.word_embeddings
    # --->>> embedding_matrix = trained_model.distilbert.embeddings.word_embeddings
    encoded_tokens = corresponding_tokenizer.encode_plus(question, None, add_special_tokens=True,
                                                         max_length=512,
                                                         pad_to_max_length=True,
                                                         return_token_type_ids=True,
                                                         truncation=True)
    # --->>> token_ids = list(encoded_tokens["input_ids"].numpy()[0])
    token_ids = list(encoded_tokens["input_ids"])
    # print(embedding_matrix)  # **** Learn 30522 from here.
    # print(embedding_matrix.num_embeddings)
    vocab_size = embedding_matrix.num_embeddings # embedding_matrix.get_shape()[0]

    # convert token ids to one hot. We can't differentiate wrt to int token ids hence the need for one hot representation
    token_ids_tensor = tf.constant([token_ids], dtype='int32')
    token_ids_tensor_one_hot = tf.one_hot(token_ids_tensor, vocab_size)

    with tf.GradientTape(watch_accessed_variables=False) as tape:
        # (i) watch input variable
        tape.watch(token_ids_tensor_one_hot)

        # multiply input model embedding matrix; allows us do backprop wrt one hot input
        inputs_embeds = embedding_matrix(token_ids_tensor_one_hot) # BIG PROBLEM -> {{{TypeError: embedding(): argument 'indices' (position 2) must be Tensor, not tensorflow.python.framework.ops.EagerTensor}}}
        print(inputs_embeds)
        # --->>> inputs_embeds = tf.matmul(token_ids_tensor_one_hot, embedding_matrix)

        # (ii) get prediction
        temp_prediction = trained_model(
            {"inputs_embeds": inputs_embeds, "token_type_ids": encoded_tokens["token_type_ids"],
             "attention_mask": encoded_tokens["attention_mask"]}).squeeze()
        big_val, big_idx = torch.max(temp_prediction.data, dim=1)

        # (iii) get gradient of input with respect to both start and end output
        gradient_non_normalized = tf.norm(
            tape.gradient(big_idx, token_ids_tensor_one_hot), axis=2)

        # (iv) normalize gradient scores and return them as "explanations"
        gradient_tensor = (
                gradient_non_normalized /
                tf.reduce_max(gradient_non_normalized)
        )
        gradients = gradient_tensor[0].numpy().tolist()

        token_words = corresponding_tokenizer.convert_ids_to_tokens(token_ids)
        token_types = list(encoded_tokens["token_type_ids"].numpy()[0])

        return gradients, token_words, token_types


def plot_gradients(tokens, token_types, gradients, title):
    plt.figure(figsize=(21, 3))
    xvals = [x + str(i) for i, x in enumerate(tokens)]
    colors = [(0, 0, 1, c) for c, t in zip(gradients, token_types)]
    edgecolors = ["black" if t == 0 else (0, 0, 1, c) for c, t in zip(gradients, token_types)]
    # colors =  [  ("r" if t==0 else "b")  for c,t in zip(gradients, token_types) ]
    plt.tick_params(axis='both', which='minor', labelsize=29)
    p = plt.bar(xvals, gradients, color=colors, linewidth=1, edgecolor=edgecolors)
    plt.title(title)
    p = plt.xticks(ticks=[i for i in range(len(tokens))], labels=tokens, fontsize=12, rotation=90)


class DistillBERTClass(torch.nn.Module):
    def __init__(self):
        super(DistillBERTClass, self).__init__()
        self.l1 = DistilBertModel.from_pretrained("distilbert-base-uncased")
        self.pre_classifier = torch.nn.Linear(768, 768)
        self.dropout = torch.nn.Dropout(0.3)
        self.classifier = torch.nn.Linear(768, 28)

    def forward(self, input_ids, attention_mask):
        output_1 = self.l1(input_ids=input_ids, attention_mask=attention_mask)
        hidden_state = output_1[0]
        pooler = hidden_state[:, 0]
        pooler = self.pre_classifier(pooler)
        pooler = torch.nn.ReLU()(pooler)
        pooler = self.dropout(pooler)
        output = self.classifier(pooler)
        return output


model = torch.load('./models/pytorch_distilbert_mathtemplates.bin')
model.to(device)

df = pd.read_json('./data/alg514.json')
df = df[['sQuestion', 'templateType']]
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-cased')

gradients, tokens, token_types = get_gradient_for_single_question(df.sQuestion[0], model, tokenizer)

token_subset = -60
plot_gradients(tokens, token_types, gradients, "Q: " + df.sQuestion[0])
plot_gradients(tokens[token_subset:], token_types[token_subset:], gradients[token_subset:],
               "Q: " + df.sQuestion[0] + " --> Remaining part")
