import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re

book = epub.read_epub('FB.epub')

titleClasses = ['lh1', 'lh']
subtitleClass = 'ul'
flavorAffinitiesClass = 'h4'
attributes = ['Season', 'Taste', 'Weight', 'Volume', 'Techniques', 'Function']

class Ingredient:
    Name = ''

    Season = []
    Taste = []
    Weight = []
    Volume = []
    Techniques = []
    Function = []

    Ingredients = {}
    FlavorAffinities = None

    # Constructor
    def __init__(self, Name):
        self.Name = Name

        self.Season = []
        self.Taste = []
        self.Weight = []
        self.Volume = []
        self.Techniques = []
        self.Function = []
        self.Ingredients = {}
        self.FlavorAffinities = None

# Iterate through the document files in the book
for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    if (item.get_name().__contains__('chap-3')):
        content = item.get_content()
        parsed = BeautifulSoup(content, 'html.parser')
        items = parsed.find_all('p')
        ingredient = None
        for paragraph in items:
            if (paragraph is not None and paragraph.has_attr('class')):
                if (paragraph['class'][0] in titleClasses or paragraph.text.__contains__('(See')):
                    title = paragraph.text
                    # Remove (See xy) from titles
                    if (title.__contains__('(See')):
                        splitTitle = re.split('(\(See+)', title)
                        title = splitTitle[0]
                    if (ingredient is not None):
                        print('\n' + ingredient.Name)
                        print("\nIngredients:")
                        print(ingredient.Ingredients)
                        print("\nFlavor Affinities:")
                        print(ingredient.FlavorAffinities)
                    ingredient = Ingredient(title)
                elif (paragraph['class'][0] == subtitleClass):
                    title = paragraph.text
                    if (ingredient.FlavorAffinities is not None):
                        ingredient.FlavorAffinities.append(title)
                    else:
                        isStrong = paragraph.find('strong') is not None
                        # Remove (See xy) from titles
                        if (title.__contains__('(See')):
                            splitTitle = re.split('(\(See+)', title)
                            title = splitTitle[0]
                        score = 0
                        if (isStrong):
                            if (title[0] == '*'):
                                score = 3
                            elif (title.isupper()):
                                score = 2
                            else:
                                score = 1
                        else:
                            ingredient.Ingredients[title] = score
                elif (paragraph['class'][0] == flavorAffinitiesClass and paragraph.text == "Flavor Affinities"):
                    ingredient.FlavorAffinities = []