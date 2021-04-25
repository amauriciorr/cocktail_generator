import pytz
import argparse
import pandas as pd
import numpy as np
from copy import copy
from datetime import datetime as dt
import torch
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, TensorDataset, RandomSampler
from transformers import GPT2LMHeadModel, GPT2Tokenizer, AdamW

TIMEZONE = pytz.timezone('America/New_York')

def get_splits(df, train_percent=.8, validate_percent=.1, validate_only=True, seed=None):
    # generate shuffled indices using seed
    np.random.seed(seed)
    shuffled_idx = np.random.permutation(df.index)
    # determine indices for partitioning df
    rows = len(df.index)
    train_idx = int(train_percent * rows)
    if validate_only:
        train = df.iloc[shuffled_idx[:train_idx]]
        validate = df.loc[shuffled_idx[train_idx:]]
        return train, validate
    else:
        validate_idx = int(validate_percent * rows) + train_idx
        train = df.iloc[shuffled_idx[:train_idx]]
        validate = df.loc[shuffled_idx[train_idx:validate_idx]]
        test = df.loc[shuffled_idx[validate_idx:]]
        return train, validate, test

def tokenize_data(df, tokenizer, max_sentence_length=330):
    df_ = df.copy()
    df_.fillna(' ', inplace=True)
    recipes = df_['title'] + '\n' + df_['description'] + '\n' + df_['directions'] \
              + tokenizer.eos_token
    tokenized_recipes = []
    attn_masks = []
    labels = []
    for _, recipe in recipes.items():
        encoded = tokenizer.encode_plus(recipe, padding='max_length', 
                                        truncation=True,
                                        max_length=max_sentence_length)
        tokenized_recipes.append(encoded['input_ids'])
        attn_masks.append(encoded['attention_mask'])
        labels.append(encoded['input_ids'])
    tokenized_recipes = torch.tensor(tokenized_recipes, dtype=torch.long)
    attn_masks = torch.tensor(attn_masks, dtype=torch.long)
    labels = torch.tensor(labels, dtype=torch.long)
    return TensorDataset(tokenized_recipes, attn_masks, labels)

def calculate_perplexity(loss):
    '''
    perplexity is essentially the exponentiation of entropy. it is a metric
    inversely proportional to the probability that the model assigns to a set of sequences; 
    i.e. a measurement of how well a probability model predicts a sample. intuitively, 
    perplexity measures the average rank of the true next-token, when tokens are ordered 
    by the model's conditional probabilities
    '''  
    perplexity = float(2**(loss/np.log(2)))
    return perplexity

def format_perplexity(ppl):
    '''
    helper for logging perplexity at each step. 
    accounting for edge-case of returning infinity
    '''
    try:
        return "{:.4f}".format(ppl)
    except:
        return str(ppl)

def get_loader(dataset, batch_size):
    sampler = RandomSampler(dataset)
    loader = DataLoader(dataset,sampler=sampler, batch_size=batch_size)
    return loader

class trainer(object):
    # def __init__(self, device, model, criterion, train_data, validation_data):
    # doesn't look like I need a criterion for this since GPT2 computes and 
    # returns loss
    def __init__(self, device, model, train_data, validation_data):
        self.device = device
        self.model = model
        self.train_data = train_data
        self.validation_data = validation_data

    def train_step(self, batch_size, optimizer):
        self.model.to(self.device)
        self.model.train()
        train_loss_cache = []
        train_loader = get_loader(self.train_data, batch_size)
        for step, batch in enumerate(train_loader):
            batch = tuple(t.to(self.device) for t in batch)
            input_ids, attention_masks, labels = batch
            loss = model(input_ids, labels = labels, attention_mask = attention_masks)[0]
            train_loss_cache.append(loss.item())
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            avg_train_loss = np.mean(train_loss_cache)
            # dataset is small, coupled with goal to use a larger batch
            # results in less steps
            if step % 25 == 0:
                print('{} | perplexity: {} | loss: {}'.format(dt.now(tz=TIMEZONE),
                                                              format_perplexity(avg_train_loss),
                                                              avg_train_loss))

        # add logging for certain number of steps
    def validate_step(self, batch_size):
        self.model.to(self.device)
        self.model.eval()
        val_loss_cache = []
        validation_loader = get_loader(self.validation_data, batch_size)
        for step, batch in enumerate(validation_loader):
            batch = tuple(t.to(self.device) for t in batch)
            input_ids, attention_masks, labels = batch
            loss = model(input_ids, labels = labels, attention_mask = attention_masks)[0]
            val_loss_cache.append(loss.item())
        avg_val_loss = np.mean(val_loss_cache)
        print('{} | validation perplexity: {}'.format(dt.now(tz=TIMEZONE), 
                                                      format_perplexity(avg_val_loss)))
        return avg_val_loss

    def train(self, batch_size, epochs, optimizer, patience, save_path='./'):
        best_val_loss = np.inf
        patience_counter = 0
        for epoch in range(epochs):
            print('{} | Epoch {}'.format(dt.now(tz=TIMEZONE), epoch + 1))
            self.train_step(batch_size, optimizer)
            previous_val_loss = copy(best_val_loss)
            avg_val_loss = self.validate_step(batch_size)
            if avg_val_loss < best_val_loss:
                best_val_loss = copy(avg_val_loss)
                print('{} | Validation loss: {}'.format(dt.now(tz=TIMEZONE), best_val_loss))
            if patience_counter > patience:
                print('{} | Stopping early.'.format(dt.now(tz=TIMEZONE)))
            if best_val_loss < previous_val_loss:
                print('{} | Saving model...'.format(dt.now(tz=TIMEZONE)))
                torch.save({'model': self.model.state_dict()}, save_path + 'cocktail_bot.pt')
                patience_counter = 0
            else:
                patience_counter += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Build cocktail bot')
    parser.add_argument('--max_sentence_length',
                        type=int,
                        default=128,
                        help='Max sequence length for RoBERTa tokenizing and subsequent encoding.')
    parser.add_argument('--num_epochs',
                            type=int,
                            default=20,
                            help='Number of epochs to train model.')
    parser.add_argument('--learning_rate',
                        type=float,
                        default=0.001,
                        help='Controls how much we are adjusting the weights of our network with\
                              respect to the loss gradient.')
    parser.add_argument('--weight_decay',
                        type=float,
                        default=0,
                        help='L2 regularization penalty. Causes weights to exponentially decay\
                              to zero.')
    parser.add_argument('--batch_size',
                        type=int,
                        default=32,
                        help='Size of batch, i.e. size of data partitions')
    parser.add_argument('--patience', 
                        type=int,
                        default=5,
                        help='Max patience for whether or not to continue training process.')
    parser.add_argument('--model_path', 
                        type=str,
                        default='./',
                        help='Path to load fine-tuned model checkpoint.')
    args = parser.parse_args()
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = GPT2LMHeadModel.from_pretrained('gpt2-medium')
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2-medium')
    tokenizer.pad_token = tokenizer.eos_token

    cocktail_recipes_df = pd.read_csv('cocktails.csv')
    train_set, validation_set = get_splits(cocktail_recipes_df)
    train_tokenized = tokenize_data(train_set, tokenizer, args.max_sentence_length)
    validation_tokenized = tokenize_data(validation_set, tokenizer, args.max_sentence_length)

    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    model_trainer = trainer(device, model, train_tokenized, validation_tokenized)
    model_trainer.train(args.batch_size, args.num_epochs, optimizer, args.patience, save_path=args.model_path)
