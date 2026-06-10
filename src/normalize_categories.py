
CATEGORY_MAP = {
    'restaurante': ('Restauración', 'restaurante'),
    'bar notable': ('Bar', 'bar notable'),
    'bar tematico': ('Bar', 'bar temático'),
    'bar temático': ('Bar', 'bar temático'),
    'feria itinerante': ('Espacios', 'feria itinerante'),
    'mercado gastronomico': ('Espacios', 'mercado gastronómico'),
    'mercado gastronómico': ('Espacios', 'mercado gastronómico'),
    'mercado historico': ('Espacios', 'mercado histórico'),
}

def normalize_category(value):
    key = str(value or '').strip().lower()
    return CATEGORY_MAP.get(key, ('Sin clasificar', key or 'sin dato'))
