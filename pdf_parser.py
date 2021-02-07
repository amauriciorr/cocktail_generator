import re
import pandas as pd
import pickle as pkl
from copy import copy
from datetime import datetime as dt
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

TITLE_REGEX = re.compile(r'\d\. [A-Z\s]{1,}\n\n')
BARTENDER_TAGLINE = re.compile(r'\n\n1000 BEST BARTENDER’S RECIPES\n\n')
# GARNISH_REGEX = re.compile(r'(?<=Garnish)[\s\n:\w]{1,}(?=\n)')

INGREDIENT_FIELD_REGEX = re.compile(r'\n{1,}Ingredients')
EXCLUDE = re.compile(r'\nName|\nCategory|\nGlass')
GARNISH_REPLACE = re.compile(r'Garnish\s{1,}\n{1,}:?')
BOS_TITLE_REGEX = re.compile(r'\s[A-Z\s\Wd]{2,}\n')
BOS_TAGLINE = re.compile(r'\d{1,}\n\n?MR. BOSTON: OFFICIAL BARTENDER’S GUIDE\n\n?\s?')
FRACTION_SYMBOLS = {'½': ' 1/2 ', '⅓': ' 1/3 ', '⅔': ' 2/3 ',
                    '¼': ' 1/4 ', '¾': ' 3/4 ', '⅕': ' 1/5 ',
                    '⅖': '2/5', '⅗': ' 3/5 ', '⅘': ' 4/5 ', 
                    '⅙': ' 1/6 ', '⅚': ' 5/6 ', '⅛': ' 1/8 ',
                    '⅜': ' 3/8 ', '⅝':' 5/8', '⅞': ' 7/8 ',
                    '¹⁄': ' 1/'}

def read_pdf(file, log):
    parsed_pages = []
    output_string = StringIO()
    resource_manager = PDFResourceManager()
    device = TextConverter(resource_manager, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(resource_manager, device)
    print('{} | Parsing PDF...'.format(dt.now()))
    for idx, page in enumerate(PDFPage.get_pages(file)):
        if log:
            if idx % 100 == 0:
                print('Parsing page: {}'.format(idx + 1))
        interpreter.process_page(page)
        parsed_pages.append(output_string.getvalue())
        output_string.truncate(0)
        output_string.seek(0)
    print('{} | Finished parsing {} pages.'.format(dt.now(), len(parsed_pages)))
    return parsed_pages

class bartender_parser:
    def __init__(self, pdf, start_page, end_page, log=False):
        self.pdf_pages = read_pdf(pdf, log)
        self.start_page = start_page
        self.end_page = end_page
        self.raw_recipes = None
        self.recipes = None

    def extract_recipes(self, page):
        recipes = []
        titles = list(TITLE_REGEX.finditer(page))
        if len(titles) > 2:
            for i in range(len(titles) - 1):
                first_recipe, second_recipe = titles[i:i+2]
                start = first_recipe.span()[0]
                end = second_recipe.span()[0]
                recipes.append(page[start:end])
            recipes.append(page[end:])
        elif len(titles) == 2:
            recipe_break = titles[1].span()[0]
            recipes.append(page[:recipe_break])
            recipes.append(page[recipe_break:])
        else:
            recipes.append(copy(page))
        return recipes

    def collect_recipes(self):
        recipes = []
        for page in self.pdf_pages[self.start_page:self.end_page]:
            recipe = self.extract_recipes(page)
            recipes += recipe
        self.raw_recipes = recipes

    def recipe_cleanup(self, recipe):
        # TO-DO
        pass

    def get_recipe_segments(self, recipe):
        title = TITLE_REGEX.match(recipe)
        description_start = title.span()[1]
        directions_start = re.match(r'\n\n\d\.', recipe).span()[0]
        description = recipe[description_start:directions_start]
        directions = recipe[directions_start:]
        return title.group(0), description, directions

    def create_recipe_df(self, recipes=None):
        recipe_data = []
        if not recipes:
            recipes = self.return_recipes()
        for recipe in recipes:
            title, decription, directions = self.get_recipe_segments(recipe)
            recipe_data.append([title, description, directions])
        return pd.DataFrame(recipe_data, columns = ['title', 'description', 'directions'])

    def process_recipe_df(self):
        pass
        # TO-DO   

class testament_parser:
    def __init__(self, pdf, start_page, end_page, log=False):
        self.pdf_pages = read_pdf(pdf, log)
        self.start_page = start_page
        self.end_page = end_page
        self.raw_recipes = None
        self.recipes = None

    def extract_recipes(self, page):
        recipes = []
        ingredients_field = list(INGREDIENT_FIELD_REGEX.finditer(page))
        if len(ingredients_field) > 1:
            first_recipe = page[:ingredients_field[1].span()[0]]
            second_recipe = page[:ingredients_field[0].span()[0]] + page[ingredients_field[1].span()[0]:]
            recipes.append(first_recipe)
            recipes.append(second_recipe)
        elif ingredients_field:
            recipes.append(copy(page))
        return recipes

    def recipe_cleanup(self, recipe):
        # leaving as a separate function in case
        # I'd like to expand the clean-up
        recipe = EXCLUDE.sub('', recipe)
        recipe = GARNISH_REPLACE.sub('Garnish: ', recipe)
        recipe = re.sub(r'\n\s', '\n', recipe)
        return recipe

    def collect_recipes(self):
        # rather than worry about capturing every single
        # recipe and over-engineering, I've opted to exclude
        # recipes that have overly long descriptions
        # i.e. those that spill onto subsequent pages
        recipes = []
        recipes_to_use = []
        for page in self.pdf_pages[self.start_page:self.end_page]:
            recipe = self.extract_recipes(page)
            recipes += recipe
        for recipe in recipes:
            if INGREDIENT_FIELD_REGEX.search(recipe):
                recipe = self.recipe_cleanup(recipe)
                recipes_to_use.append(recipe)
        self.raw_recipes = recipes_to_use

    def get_recipe_segments(self, recipe):
        pass
        # title_and_description = recipe[:directions_start[0]]
        # directions = recipe[directions_start[1]:]
        '''note to self: separate by taking everything
        after garnish as directions. then ingredients.
        take last line of ingredients and move to directions. 
        '''

class boston_parser:
    def __init__(self, pdf, start_page, end_page, log=False):
        self.pdf_pages = read_pdf(pdf, log)
        self.start_page = start_page
        self.end_page = end_page
        self.raw_recipes = None
        self.recipes = None

    def replace_fractions(self, page):
        for key, value in FRACTION_SYMBOLS.items():
            page = re.sub(r'{}'.format(key), value, page)
        return page

    def extract_recipes(self, page):
        recipes = []
        titles = list(BOS_TITLE_REGEX.finditer(page))
        if len(titles) > 2:
            for i in range(len(titles) - 1):
                first_recipe, second_recipe = titles[i:i+2]
                start = first_recipe.span()[0]
                end = second_recipe.span()[0]
                recipes.append(page[start:end])
            recipes.append(page[end:])
        elif titles == 2:
            recipe_break = titles[1].span()[0]
            recipes.append(page[:recipe_break])
            recipes.append(page[recipe_break:])
        else:
            recipes.append(copy(page))
        return recipes

    def title_fix(self, page):
        split_page = page.split('\n')
        if BOS_TITLE_REGEX.search(split_page[0]) and BOS_TITLE_REGEX.search(split_page[1]):
            fixed_page = [split_page[0] + ' ' + split_page[1]] + split_page[2:]
            fixed_page = '\n'.join(fixed_page)
        else:
            fixed_page = '\n'.join(split_page)
        return fixed_page

    def recipe_cleanup(self, page):
        page = self.replace_fractions(page)
        page = BOS_TAGLINE.sub('', page)
        page = re.sub(r'\n\n', '\n', page)
        page = re.sub(r'\n[A-Z]{1}\b', '', page)
        page = re.sub(r'\n\x0c', '', page)
        page = re.sub(r'-\n', '', page)
        page = re.sub(r'^\n\s?', '', page)
        page = self.title_fix(page)
        return page

    def collect_recipes(self):
        recipes = []
        recipes_to_use = []
        for page in self.pdf_pages[self.start_page:self.end_page]:
            page = self.recipe_cleanup(page)
            recipes.append(page)
        for recipe in recipes:
            recipes_to_use += self.extract_recipes(recipe)
        self.raw_recipes = recipes_to_use

