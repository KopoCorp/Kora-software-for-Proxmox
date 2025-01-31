# Python script: generate_kora_doc.py

import os
import sys
import ast
from rich.console import Console
from rich.table import Table

def extract_functions(script_path):
    """Extrait toutes les fonctions définies dans un fichier Python, y compris dans les classes et leurs descriptions."""
    functions = []
    descriptions = {}
    with open(script_path, "r", encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read(), filename=script_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                    docstring = ast.get_docstring(node)
                    descriptions[node.name] = docstring.strip().split("\n")[0] if docstring else ""
        except SyntaxError:
            functions.append("Erreur de syntaxe dans le fichier")
    return functions, descriptions

def generate_documentation(scripts_dir):
    """Génère une documentation esthétique pour les scripts."""
    console = Console()
    table = Table(title="Documentation des Scripts KORA")

    table.add_column("Dossier", style="blue", no_wrap=True)
    table.add_column("Nom du Script", style="cyan", no_wrap=True)
    table.add_column("Fonctions", style="magenta")
    table.add_column("Description", style="yellow")

    last_folder = None
    for root, _, files in os.walk(scripts_dir):
        parent_folder = os.path.basename(root)  # Récupère uniquement le dossier parent
        script_rows = []

        for file in files:
            if file.endswith(".py"):
                script_path = os.path.join(root, file)
                functions, descriptions = extract_functions(script_path)
                if not functions and file in ["config.py", "kora_config.py"]:
                    script_rows.append([file, "Script de configuration, pas de fonctions", ""])
                else:
                    for func in functions:
                        script_rows.append([file, func, descriptions.get(func, "")])
        
        if script_rows:
            if last_folder != parent_folder:
                table.add_row(f"[bold yellow]{parent_folder}[/bold yellow]", "", "", "")
                table.add_row("", "", "", "")
                last_folder = parent_folder
            
            for script in script_rows:
                table.add_row("", script[0], script[1], script[2])
    
    console.print(table)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 generate_kora_doc.py <chemin_vers_le_repertoire>")
        sys.exit(1)

    scripts_dir = sys.argv[1]
    if not os.path.isdir(scripts_dir):
        print(f"Le chemin spécifié n'existe pas ou n'est pas un répertoire : {scripts_dir}")
        sys.exit(1)

    generate_documentation(scripts_dir)
