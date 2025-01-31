import rich
from rich.console import Console
from rich import print
import re

def colorize_text(input_text):
    color_mappings = {
        r"#+": ("[#6C6392]", "[/#6C6392]"),
        r"\\.": ("[#FFFFFF]", "[/#FFFFFF]"),
        r"@": ("[#FFFFFF]", "[/#FFFFFF]"),
        r"<.*?>": ("[#FFFFFF]", "[/#FFFFFF]"),
        r".+": ("[#FFFFFF]", "[/#FFFFFF]"),
        r"^": ("[#FFFFFF]", "[/#FFFFFF]"),
        r"o": ("[#6C6392]", "[/#6C6392]"),
        r"O": ("[#FFFFFF]", "[/#FFFFFF]"),
        r"/(?=[^#])": ("[#FF012B]", "[/#FF012B]"),
    }

    output_text = input_text
    for pattern, (start_tag, end_tag) in color_mappings.items():
        output_text = re.sub(
            pattern,
            lambda match: f"{start_tag}{match.group(0)}{end_tag}",
            output_text
        )

    return output_text

kobot="\
                   #######@@@#######\n\
                ##########@@@##########\n\
              ####    @@@@@@@@@@@    ####\n\
             ###   @@@@@@@@@@@@@@@@@   ###\n\
             ##   @@@@@@@/////@@@@@@@   ##\n\
            ##    @@@@@@//<@>//@@@@@@    #\n\
             ##   @@@@@@@/////@@@@@@@   ##\n\
             ###   @@@@@@@@@@@@@@@@@   ###\n\
              ####   @@@@@@@@@@@@@   ####\n\
                ###   ###########   ###\n\
                   #######   ####### \n\
------------------------------------------------------- \n\
Welcome to Kora, please restart to enjoy the services !\n\
------------------------------------------------------- \n"

print(colorize_text(kobot))


