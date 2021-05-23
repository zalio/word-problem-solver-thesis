# Importing the libraries needed
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertModel, DistilBertTokenizer

# Setting up the device for GPU usage
from torch import cuda

device = 'cuda' if cuda.is_available() else 'cpu'

# Import the csv into pandas dataframe and add the headers
df = pd.read_json('./data/alg514.json')  # MODIFIED
# print(df.head())
# # Removing unwanted columns and only leaving title of news and the category which will be the target
df = df[['sQuestion', 'templateType']]  # MODIFIED
print(df.head())  # MODIFIED

# TEST TO SEE IF VALIDATION STEP 51 ERROR IS ONLY CAUSED BY NEAR THE END OF THE DATASET => ****************************
# df = df[:500]

# Defining some key variables that will be used later on in the training
MAX_LEN = 512
TRAIN_BATCH_SIZE = 4
VALID_BATCH_SIZE = 2
EPOCHS = 1
LEARNING_RATE = 1e-05
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-cased')


class Triage(Dataset):
    def __init__(self, dataframe, tokenizer, max_len):
        self.len = len(dataframe)
        self.data = dataframe
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __getitem__(self, index):
        question = str(self.data.sQuestion[index])  # MODIFIED
        question = " ".join(question.split())  # MODIFIED
        inputs = self.tokenizer.encode_plus(
            question,  # MODIFIED
            None,
            add_special_tokens=True,
            max_length=self.max_len,
            pad_to_max_length=True,
            return_token_type_ids=True,
            truncation=True
        )
        ids = inputs['input_ids']
        mask = inputs['attention_mask']

        return {
            'ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.long),
            'targets': torch.tensor(self.data.templateType[index], dtype=torch.long),  # MODIFIED
            # 'questions': torch.tensor(self.data.sQuestion[index], dtype=torch.long)  # MODIFIED
        }

    def __len__(self):
        return self.len


# Creating the dataset and dataloader for the neural network
train_size = 0.8
train_dataset = df.sample(frac=train_size, random_state=200)
test_dataset = df.drop(train_dataset.index).reset_index(drop=True)
train_dataset = train_dataset.reset_index(drop=True)

# Organize and prepare the datasets.
print("FULL Dataset: {}".format(df.shape))
print("TRAIN Dataset: {}".format(train_dataset.shape))
print("TEST Dataset: {}".format(test_dataset.shape))

training_set = Triage(train_dataset, tokenizer, MAX_LEN)
testing_set = Triage(test_dataset, tokenizer, MAX_LEN)

train_params = {'batch_size': TRAIN_BATCH_SIZE,
                'shuffle': False,
                'num_workers': 0
                }

test_params = {'batch_size': VALID_BATCH_SIZE,
               'shuffle': False,
               'num_workers': 0
               }

training_loader = DataLoader(training_set, **train_params)
testing_loader = DataLoader(testing_set, **test_params)


# Creating the customized model, by adding a drop out and a dense layer on top of distil bert to get the final output for the model.
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


# Create model.
model = DistillBERTClass()
model.to(device)

# Creating the loss function and optimizer
loss_function = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(params=model.parameters(), lr=LEARNING_RATE)


# Function to calcuate the accuracy of the model
def calcuate_accu(big_idx, targets):
    # print("big_idx =", big_idx)  #EXTRA!!!
    # print("target =", targets)  #EXTRA!!!

    n_correct = (big_idx == targets).sum().item()
    return n_correct


# Defining the training function on the 80% of the dataset for tuning the distilbert model
def train(epoch):
    tr_loss = 0
    n_correct = 0
    nb_tr_steps = 0
    nb_tr_examples = 0
    model.train()

    # Extra!!!
    # print("Training loader size = ", len(training_loader)) #MODIFIED

    for _, data in enumerate(training_loader, 0):
        ids = data['ids'].to(device, dtype=torch.long)
        mask = data['mask'].to(device, dtype=torch.long)
        targets = data['targets'].to(device, dtype=torch.long)

        # print(data)  #EXTRA!!!

        # print("ids =", ids)  #EXTRA!!!
        # print("mask = ", mask)  #EXTRA!!!

        outputs = model(ids, mask)

        # print("Outputs: ", outputs)  #EXTRA!!!

        loss = loss_function(outputs, targets)

        # print("loss:", loss)  #EXTRA!!!

        tr_loss += loss.item()
        big_val, big_idx = torch.max(outputs.data, dim=1)
        n_correct += calcuate_accu(big_idx, targets)

        nb_tr_steps += 1
        nb_tr_examples += targets.size(0)

        # Extra!!!
        print("Training step: ", _)  # MODIFIED

        if _ % 100 == 0:  # MODIFIED
            loss_step = tr_loss / nb_tr_steps
            accu_step = (n_correct * 100) / nb_tr_examples
            print(f"Training Loss per 100 steps: {loss_step}")  # MODIFIED
            print(f"Training Accuracy per 100 steps: {accu_step}")  # MODIFIED

        optimizer.zero_grad()
        loss.backward()
        # # When using GPU
        optimizer.step()

    print(f'The Total Accuracy for Epoch {epoch}: {(n_correct * 100) / nb_tr_examples}')
    epoch_loss = tr_loss / nb_tr_steps
    epoch_accu = (n_correct * 100) / nb_tr_examples
    print(f"Training Loss Epoch: {epoch_loss}")
    print(f"Training Accuracy Epoch: {epoch_accu}")

    return


# Do the actual training.
for epoch in range(EPOCHS):
    train(epoch)


# Define validation function.
def valid(model, testing_loader):
    model.eval()
    n_correct = 0
    n_wrong = 0
    total = 0
    tr_loss = 0
    nb_tr_steps = 0
    nb_tr_examples = 0

    question_list = []  # MODIFIED
    targets_list = []  # MODIFIED
    prediction_list = []  # MODIFIED

    with torch.no_grad():
        for _, data in enumerate(testing_loader, 0):
            ids = data['ids'].to(device, dtype=torch.long)
            mask = data['mask'].to(device, dtype=torch.long)
            targets = data['targets'].to(device, dtype=torch.long)
            outputs = model(ids, mask).squeeze()
            # loss = loss_function(outputs, targets)  # IGNORED FOR NOW
            # tr_loss += loss.item()  # IGNORED FOR NOW
            big_val, big_idx = torch.max(outputs.data, dim=1)
            n_correct += calcuate_accu(big_idx, targets)

            nb_tr_steps += 1
            nb_tr_examples += targets.size(0)

            # Extra!!!
            print("Validation step: ", _)  # MODIFIED

            for i in range(len(big_idx)):  # MODIFIED
                prediction_list.append(big_idx[i])  # MODIFIED
                targets_list.append(targets[i])  # MODIFIED
                question_list.append(test_dataset.sQuestion[2 * _ + i])  # MODIFIED / 2 is for testing batch size

            # TO FIX THE VALIDATION STEP 51 ERROR => *************************************************************
            if _ == 50:
                break

            if _ % 100 == 0:  # MODIFIED
                # loss_step = tr_loss / nb_tr_steps  # IGNORED FOR NOW
                accu_step = (n_correct * 100) / nb_tr_examples
                # print(f"Validation Loss per 100 steps: {loss_step}") # MODIFIED  # IGNORED FOR NOW
                print(f"Validation Accuracy per 100 steps: {accu_step}")  # MODIFIED
    # epoch_loss = tr_loss / nb_tr_steps  # IGNORED FOR NOW
    epoch_accu = (n_correct * 100) / nb_tr_examples
    # print(f"Validation Loss Epoch: {epoch_loss}")  # IGNORED FOR NOW
    print(f"Validation Accuracy Epoch: {epoch_accu}")

    temp_data_list = [question_list, targets_list, prediction_list]  # MODIFIED
    return epoch_accu, temp_data_list


# print('This is the validation section to print the accuracy and see how it performs')
# print('Here we are leveraging on the dataloader crearted for the validation dataset, the approach is using more of pytorch')

acc, temp_data = valid(model, testing_loader)
print("Accuracy on test data = %0.2f%%" % acc)

# Saving the files for re-use
output_model_file = './models/pytorch_distilbert_mathtemplates.bin'  # MODIFIED
output_vocab_file = './models/vocab_distilbert_mathtemplates.bin'  # MODIFIED

model_to_save = model
torch.save(model_to_save, output_model_file)
tokenizer.save_vocabulary(output_vocab_file)


# --------------------------TEMP DATA PRINTER------------------------------------
def print_targets_and_predictions_for_comparison(temp_data_list):
    for t in range(len(temp_data_list[0])):
        print("Test Question:", temp_data_list[0][t])
        print("Target for this Question:", temp_data_list[1][t].item())
        print("Predicted Target for this Question:", temp_data_list[2][t].item())
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


print("***********************************************************************************")
print_targets_and_predictions_for_comparison(temp_data)


