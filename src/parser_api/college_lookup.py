import pathlib
import json

parent_dir = pathlib.Path(__file__).parent.absolute()


def get_colleges():
    """ From college_abbreviations.json, retrieve mapping of colleges to abbreviations as JSON. """
    abb_dir = parent_dir / pathlib.Path("college_abbreviations.json")
    with open(str(abb_dir), 'r') as file:
        abbreviations = json.load(file)
        return abbreviations
