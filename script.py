import ebooklib
import json
from ebooklib import epub
from bs4 import BeautifulSoup
import re

# Import your source .epub file
book = epub.read_epub('source.epub')

titleClasses = ['lh1', 'lh']
subtitleClass = 'ul'
flavorAffinitiesClass = 'h4'

class Ingredient():
    Name = ''

    Season = None
    Taste = None
    Weight = None
    Volume = None
    Techniques = None
    Function = None
    Ingredients = {}
    FlavorAffinities = None

    # Constructor
    def __init__(self, Name):
        self.Name = Name

        self.Season = ''
        self.Taste = ''
        self.Weight = ''
        self.Volume = ''
        self.Techniques = ''
        self.Function = ''
        self.Ingredients = {}
        self.FlavorAffinities = None

    def printIngredient(self):
        print('\n' + self.Name)
        print("\nSeason:" + self.Season)
        print("Taste:" + self.Taste)
        print("Weight:" + self.Weight)
        print("Volume:" + self.Volume)
        print("Techniques:" + self.Techniques)
        print("Function:" + self.Function)
        print("\nIngredients:")
        print(self.Ingredients)
        print("\nFlavorAffinities:")
        print(self.FlavorAffinities)

    def toJson(self):
        j = {}
        j['Name'] = self.Name.title()

        j['Season'] = self.Season
        j['Taste'] = self.Taste
        j['Weight'] = self.Weight
        j['Volume'] = self.Volume
        j['Techniques'] = self.Techniques
        j['Function'] = self.Function

        j['Ingredients'] = self.Ingredients
        j['FlavorAffinities'] = self.FlavorAffinities
        
        return j

# Initialize the JSON Data
data = {}
data['Ingredients'] = []

ingredient = None

def handleIngredient():
    data['Ingredients'].append(ingredient.toJson())

# Iterate through the document files in the book
for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    if (item.get_name().__contains__('chap-3')):
        content = item.get_content()
        parsed = BeautifulSoup(content, 'html.parser')
        items = parsed.find_all('p')
        for paragraph in items:
            if (paragraph is not None and paragraph.has_attr('class')):
                if (paragraph['class'][0] in titleClasses or paragraph.text.__contains__('(See')):
                    title = paragraph.text
                    # Remove (See xy) from titles
                    if (title.__contains__('(See')):
                        splitTitle = re.split('(\(See+)', title)
                        title = splitTitle[0]
                    if (ingredient is not None):
                        handleIngredient()
                    ingredient = Ingredient(title)
                elif (paragraph['class'][0] == subtitleClass):
                    title = paragraph.text
                    if (ingredient.FlavorAffinities is not None):
                        ingredient.FlavorAffinities.append(title)
                    else:
                        strongTag = paragraph.find('strong')
                        # Remove (See xy) from titles
                        if (title.__contains__('(See')):
                            splitTitle = re.split('(\(See+)', title)
                            title = splitTitle[0]
                        score = 0
                        # Check if a part of the text is in bold
                        if (strongTag is not None):
                            strongTag = strongTag.text
                            if (strongTag == "Season:"):
                                ingredient.Season = title.replace("Season:", "")
                            elif (strongTag == "Taste:"):
                                ingredient.Taste = title.replace("Taste:", "")
                            elif (strongTag == "Weight:"):
                                ingredient.Weight = title.replace("Weight:", "")
                            elif (strongTag == "Volume:"):
                                ingredient.Volume = title.replace("Volume:", "")
                            elif (strongTag == "Techniques:"):
                                ingredient.Techniques = title.replace("Techniques:", "")
                            elif (strongTag == "Function:"):
                                ingredient.Function = title.replace("Function:", "")
                            # Add an ingredient
                            elif (title[0] == '*'):
                                score = 3
                            elif (title.isupper()):
                                score = 2
                            else:
                                score = 1
                        ingredient.Ingredients[title] = score
                elif (paragraph['class'][0] == flavorAffinitiesClass and paragraph.text == "Flavor Affinities"):
                    ingredient.FlavorAffinities = []
# Handle the last ingredient of the source
handleIngredient()

# Dump the json data
with open('data.json', 'w') as outfile:
    json.dump(data, outfile)