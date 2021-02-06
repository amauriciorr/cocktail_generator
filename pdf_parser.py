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
# GARNISH_REGEX = re.compile(r'(?<=Garnish)[\s\n:\w]{1,}(?=\n)')

INGREDIENT_FIELD_REGEX = re.compile(r'\n{1,}Ingredients')
EXCLUDE = re.compile(r'\nName|\nCategory|\nGlass')
GARNISH_REPLACE = re.compile(r'Garnish\s{1,}\n{1,}:?')

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

    def get_recipes(self, page):
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
            recipe = self.get_recipes(page)
            recipes += recipe
        self.raw_recipes = recipes

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

    def get_recipes(self, page):
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
            recipe = self.get_recipes(page)
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
    def __init__(self, pdf, log=False):
        self.pdf_pages = read_pdf(pdf, log)
        self.raw_recipes = None
        self.recipes = None

