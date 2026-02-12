def parse_motif_name(motif_name: str):
    """
    Parsea el nombre de un motivo para extraer el nombre base y los argumentos.
    Por ejemplo:
        'cycle_4' -> ('cycle', [4])
        'house'   -> ('house', [])
    Args:
        motif_name (str): Nombre del motivo, posiblemente con argumentos separados por '_'.
    Returns:
        tuple: (nombre_base, lista_de_argumentos)
    """
    parts = motif_name.split('_')
    base = parts[0]
    args = [int(p) for p in parts[1:]] if len(parts) > 1 else []
    return base, args
