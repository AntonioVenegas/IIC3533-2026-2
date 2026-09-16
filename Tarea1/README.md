# Setup

Para este proyecto es necesario tener la versión 3.13.15 de python (se puede usar pyenv o conda si es que prefieren uno sobre el otro)

# Usando conda

```bash
conda create -n tarea1-hpc python=3.13 -y
conda activate tarea1-hpc
conda install numpy matplotlib joblib threadpoolctl -y
```

# Usando venv

## 1. Crear el entorno virtual

**Linux / macOS**

```bash
python3 -m venv venv
```

**Windows**

```bash
python -m venv venv
```

## 2. Activar el entorno virtual

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows (cmd)**

```bash
venv\Scripts\activate.bat
```

**Windows (PowerShell)**

```powershell
venv\Scripts\Activate.ps1
```

Una vez activado, deberías ver `(venv)` al inicio de la línea de comandos.

## 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Revisar la instalación

Para ver las librerías instaladas:

```
pip list
```

## 5. Desactivar el entorno virtual

Cuando termines de trabajar:

```bash
deactivate
```
