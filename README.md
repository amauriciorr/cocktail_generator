# Cocktail recipe generator using GPT2
Built using cocktail recipe PDFs I found on the web:
* _1000 Best Bartender Recipes: The Essential Collection for the Best Home Bars and Mixologists_ by Suzi Parker
* _Old Mr. Boston Deluxe Official Bartender's Guide_ by Leo Cotton
* misc. recipes from my coworkers

## Files explained
* `pdf_parser.py` - contains classes specific to different source materials mentioned above. this script is responsible for cleaning, pre-processing, and structuring data for training bartender
* `bartender_trainer.py` - contains standard training utils (i.e. tokenizer, data splits, training/validation steps, Trainer class). this script trains our bartender bot.

