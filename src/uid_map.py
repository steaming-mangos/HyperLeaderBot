from json import load
from bidict import bidict


def load_map_bidict() -> bidict:
    """
    Load the HyperDemon UID to Discord UID map as a bi-directional dictionary.

    See [`load_map_dict`] for key/value when not using bidict.inverse().

    :returns: dict :: HD UID - Discord UID map
    """
    id_map_bidict = bidict(load_map_dict())
    return id_map_bidict


def load_map_dict() -> dict:
    """
    Load the HyperDemon UID to Discord UID map.

    Key: Hyper Demon UID
    Value: Discord UID

    :returns: dict :: HD UID - Discord UID map
    """
    with open("id_dictionary.json", "r") as outfile:
        id_map = load(outfile)

    # should all just be numeric IDs: casting should be ok
    id_map = {int(k): int(v) for k, v in id_map.items()}
    return id_map
