from typing import Literal

INSTRUMENT = Literal['SPIROU', 'ESPADONS', 'MEGACAM']

required_mag_by_instrument: dict[INSTRUMENT, str] = {
    'SPIROU': 'H',
    'ESPADONS': 'V',
    'MEGACAM': 'AB',
}
