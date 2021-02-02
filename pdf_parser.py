import re
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

def read_pdf(file, log=False):
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
    print('{} | Finished parsing.'.format(dt.now()))
    return parsed_pages

def get_recipes(page):
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

def get_recipe_segments(recipe):
    title = TITLE_REGEX.match(recipe)
    description_start = title.span()[1]
    directions_start = re.match(r'\n\n\d\.', recipe).span()[0]
    description = recipe[description_start:directions_start]
    directions = recipe[directions_start:]
    return title.group(0), description, directions
