from typing import Literal

INSTRUMENT = Literal['SPIROU', 'ESPADONS', 'MEGACAM']

required_mag_by_instrument: dict[INSTRUMENT, str] = {
    'SPIROU': 'H',
    'ESPADONS': 'V',
    'MEGACAM': 'AB',
}

def entity_desc(entity, prefix: str) -> str:
    parts = []
    if 'label' in entity:
        parts.append(f"{prefix}{entity['label']}")
    if 'name' in entity:
        parts.append(f"{entity['name']}")
    start = " - ".join(parts)
    if start:
        return f"{start} [token = {entity['token']}]"
    return f"[token = {entity['token']}]"
