# focus-title
1. Instalar dependencias:
```bash
pip install -r requirements.txt
```
2. Ejecutar la aplicación:
```bash
python app.py
```

3. Generar .exe con flet
```bash
flet pack app.py
```

4. generar con icono
```bash
pyinstaller --name "focus-title" --icon "icon.ico" --onefile app.py
```
```bash
pyinstaller --name "focus-title" --icon "icon.png" --onefile app.py
```

