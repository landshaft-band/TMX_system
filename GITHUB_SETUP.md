# Публикация проекта на GitHub

На текущей машине команды `git` и `gh` не найдены в PATH. Перед публикацией нужно установить Git или GitHub Desktop.

## Вариант 1: GitHub Desktop

1. Установите GitHub Desktop.
2. Выберите `File` -> `Add local repository`.
3. Укажите папку проекта:

```text
C:\Users\winda\Documents\diplom
```

4. Если GitHub Desktop предложит создать репозиторий, согласитесь.
5. Проверьте, что в commit не попали папки:
   - `.venv`;
   - `build`;
   - `dist`;
   - `__pycache__`;
   - `.idea`;
   - PDF-файлы из `reports`.
6. Сделайте первый commit.
7. Нажмите `Publish repository`.

## Вариант 2: Git CLI

После установки Git откройте PowerShell в папке проекта и выполните:

```powershell
git init
git add .
git commit -m "Initial Wagon WMS MES MVP"
git branch -M main
git remote add origin https://github.com/<your-login>/<repo-name>.git
git push -u origin main
```

Если репозиторий уже создан на GitHub, используйте его URL вместо примера.

## Проверка перед публикацией

```powershell
.\.venv\Scripts\python.exe -m compileall main.py ui data services models
```

## Что не нужно загружать в GitHub

Это уже исключено в `.gitignore`:

- виртуальное окружение `.venv`;
- результаты сборки `build` и `dist`;
- кеши Python;
- IDE-настройки;
- сгенерированные PDF-отчёты.

## Как собрать EXE после клонирования

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
.\build_exe.ps1
```
