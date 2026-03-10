import traceback
try:
    with open('alembic_error.txt', 'r', encoding='utf-16') as f:
        content = f.read()
        print(content[-2000:])
except Exception as e:
    with open('alembic_error.txt', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        print(content[-2000:])
