# Image Kestra actuellement utilisée par le projet BottleNeck.
# Le digest permet de conserver la même version de base.
FROM kestra/kestra@sha256:bc2e8b5c639c3ff1f7ba9c1aadef4686a87669895a1d80c23d01c58d45785914

# Installation des dépendances Python pendant la construction
# de l'image, et non pendant l'exécution du workflow.
USER root

# Copier la liste des bibliothèques Python.
COPY requirements.txt /tmp/bottleneck-requirements.txt

# Installer les versions définies dans requirements.txt.
RUN /usr/bin/python3 -m pip install \
    --no-cache-dir \
    --break-system-packages \
    -r /tmp/bottleneck-requirements.txt

# Revenir à l'utilisateur non administrateur de Kestra.
USER kestra