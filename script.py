import ebooklib
import json
from ebooklib import epub
from bs4 import BeautifulSoup
import re

# Import your source .epub file
book = epub.read_epub('source.epub')

titleClasses = ['lh1', 'lh']
subtitleClasses = ['ul', 'ul1', 'ul2', 'ul3']
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
    Avoid = None

    # Constructor
    def __init__(self, Name):
        self.Name = Name

        self.Season = ''
        self.Taste = ''
        self.Weight = ''
        self.Volume = ''
        self.Function = ''
        self.Ingredients = {}
        self.Techniques = []
        self.FlavorAffinities = None
        self.Avoid = None

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
        print("\nAvoid:")
        print(self.Avoid)

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
        j['Avoid'] = self.Avoid
        
        return j

# Initialize the JSON Data
data = {}
data['Ingredients'] = []

ingredient = None

def handleIngredient():
    data['Ingredients'].append(ingredient.toJson())
    if (ingredient.Avoid is not None):
        ingredient.printIngredient()

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
                elif (subtitleClasses.__contains__(paragraph['class'][0])):
                    title = paragraph.text
                    if (ingredient.FlavorAffinities is not None):
                        ingredient.FlavorAffinities.append(title)
                    elif (ingredient.Avoid is not None):
                        ingredient.Avoid.append(title)
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
                            if (strongTag == "AVOID"):
                                # Initialize Avoid list
                                ingredient.Avoid = []
                            elif (strongTag == "Season:"):
                                ingredient.Season = title.replace("Season:", "")
                            elif (strongTag == "Taste:"):
                                ingredient.Taste = title.replace("Taste:", "")
                            elif (strongTag == "Weight:"):
                                ingredient.Weight = title.replace("Weight:", "")
                            elif (strongTag == "Volume:"):
                                ingredient.Volume = title.replace("Volume:", "")
                            elif (strongTag == "Techniques:"):
                                techniques = title.replace("Techniques:", "").strip()
                                ingredient.Techniques = techniques.split(', ')
                            elif (strongTag == "Function:"):
                                ingredient.Function = title.replace("Function:", "")
                            else:
                                # Add an ingredient
                                if (title[0] == '*'):
                                    score = 3
                                    # Remove *
                                    title = title[1:]
                                elif (title.isupper()):
                                    score = 2
                                    title = title.title
                                else:
                                    score = 1
                                ingredient.Ingredients[title] = score
                        else:
                            ingredient.Ingredients[title] = score
                elif (paragraph['class'][0] == flavorAffinitiesClass and paragraph.text == "Flavor Affinities"):
                    ingredient.FlavorAffinities = []
# Handle the last ingredient of the source
handleIngredient()

# Dump the json data
with open('data.json', 'w') as outfile:
    json.dump(data, outfile)