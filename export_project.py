import os

# Nom du fichier de sortie
OUTPUT_FILE = "projet_complet.txt"

# Dossiers et fichiers à IGNORER (pour ne pas polluer l'analyse)
IGNORE_DIRS = {'.git', '__pycache__', 'venv', '.devcontainer', '.pytest_cache', 'migrations'}
IGNORE_FILES = {'.env', 'poetry.lock', 'package-lock.json', 'export_project.py', '.DS_Store', 'projet_complet.txt'}
# On ignore .env pour la SÉCURITÉ (ne jamais partager ses mots de passe)

def export_project():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        outfile.write("=== STRUCTURE DU PROJET ===\n")
        
        # Étape 1 : Écrire l'arborescence (Tree view)
        for root, dirs, files in os.walk("."):
            # Filtrer les dossiers ignorés
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            level = root.replace(".", "").count(os.sep)
            indent = " " * 4 * (level)
            outfile.write(f"{indent}{os.path.basename(root)}/\n")
            subindent = " " * 4 * (level + 1)
            for f in files:
                if f not in IGNORE_FILES and not f.endswith('.pyc'):
                    outfile.write(f"{subindent}{f}\n")
        
        outfile.write("\n\n=== CONTENU DES FICHIERS ===\n")

        # Étape 2 : Écrire le contenu de chaque fichier pertinent
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file in IGNORE_FILES or file.endswith('.pyc'):
                    continue
                
                # On se concentre sur les fichiers de code et config importants
                if file.endswith(('.py', '.sql', '.yml', '.yaml', '.txt', '.md', 'Dockerfile')):
                    file_path = os.path.join(root, file)
                    outfile.write(f"\n\n{'='*20} FICHIER : {file_path} {'='*20}\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"Erreur de lecture : {e}")

    print(f"✅ Terminé ! Tout le projet a été sauvegardé dans '{OUTPUT_FILE}'.")
    print("Tu peux maintenant télécharger ce fichier et l'envoyer à Gemini.")

if __name__ == "__main__":
    export_project()