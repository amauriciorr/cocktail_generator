# Cocktail recipe generator using GPT2 🍸 🥃 🍹
Built using cocktail recipe PDFs I found on the web:
* _1000 Best Bartender Recipes: The Essential Collection for the Best Home Bars and Mixologists_ by Suzi Parker
* _Old Mr. Boston Deluxe Official Bartender's Guide_ by Leo Cotton
* misc. recipes from my coworkers

## Files explained
* `pdf_parser.py` - contains classes specific to different source materials mentioned above. this script is responsible for cleaning, pre-processing, and structuring data for training bartender
* `bartender_trainer.py` - contains standard training utils (i.e. tokenizer, data splits, training/validation steps, Trainer class). this script trains our bartender bot.
* `cocktail_bot.py` - generates random cocktail at runtime

## Example generated cocktails
Below are cocktail recipes generated using GPT2 trained on cocktail recipes; each recipe was formatted to include clear `TITLE`, `DESCRIPTION`, and `DIRECTIONS` sections. A list of randomly generated recipes can be found in the `recipes/` directory. Additional gifs displaying recipe generation can be found in `assets/`.

### Bullwizard
![bullwizard](/assets/bullwizard.gif) 
```
TITLE: BULLWIZARD
DESCRIPTION: 1 1/2  ounce Whiskey (Straight Rye) 
1 ounce Lemon Juice 
 1/4  ounce Orange Juice 
 1/4  ounce Superﬁ ne Sugar  
(or Simple Syrup) 
1 ounce Lime Juice
DIRECTIONS: Shake with ice and strain  
into chilled cocktail glass. Garnish with a  
liqueur and a lemon twist.
```

### Bourbon Collins
```
TITLE: BOURBON COLLINS
DESCRIPTION: 1 1/2  ounce Gin 
1 ounce Triple Sec
DIRECTIONS: Shake with ice and strain  
into chilled cocktail glass.  
Garnish with a  
twist of lemon peel.
```

### Forever Dream
```
TITLE: FOREVER DREAM
DESCRIPTION: 1 1/2  ounce Whiskey (Bourbon) 
 1/2  ounce Lemon Juice 
 1/2  ounce Orange Juice
DIRECTIONS: Shake with ice and strain  
into chilled cocktail glass.  
Garnish with a lemon twist.
```

### Gin & Lemonade
```
TITLE: GIN AND LEMONADE
DESCRIPTION: 2 ounce Gin 
1 tbsp. Lemon Juice
DIRECTIONS: Club Soda 
Shake ﬁ rst three ingredients  
with ice and strain into  ice ﬁ lled highball  
glass. Fill with club soda  
and stir.
```

### Martini Sour
```
TITLE:  MARTINI SOUR
DESCRIPTION: Named for a famous Peruvian drink, this is a favorite among the
Vietnamese.

2 ounces vodka
2 ounces sour mix
DIRECTIONS:  Fill cocktail shaker with ice.
 Add vodka, sour mix, and bitters.
 Shake.
 Strain into a chilled martini glass.
 ```
