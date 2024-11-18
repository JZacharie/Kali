# Utilisation de l'image de base Python 3.12
FROM python:3.12

# Création du répertoire de travail dans le conteneur
WORKDIR /app

# Copie du fichier requirements.txt dans le répertoire de travail
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie de l'application dans le répertoire de travail
COPY main.py .
EXPOSE 7860

# Commande pour lancer l'application
CMD ["python", "main.py"]