import torch
from datetime import datetime
from transformers import GPT2LMHeadModel, GPT2Tokenizer

def log_message(msg):
    print('{} | {}'.format(datetime.now(), msg))

def generate_cocktail():
    log_message('loading GPT2 base...')
    model = GPT2LMHeadModel.from_pretrained('gpt2-medium')
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2-medium')
    tokenizer.pad_token = tokenizer.eos_token

    log_message('loading cocktail knowledge...')
    checkpoint = torch.load('cocktail_bot.pt', map_location='cpu')
    model.load_state_dict(checkpoint['model'])

    log_message('generating cocktail')
    recipe_start = "TITLE:"
    recipe_start = tokenizer(recipe_start, return_tensors= 'pt')
    recipe = model.generate(**recipe_start, max_length=250, top_p=0.9, pad_token_id=tokenizer.eos_token_id, do_sample=True).tolist()[0][:-1]

    log_message('Coming right up!')
    print(tokenizer.decode(recipe))

if __name__ == '__main__':
    generate_cocktail()