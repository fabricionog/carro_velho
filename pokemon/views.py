from concurrent.futures import ThreadPoolExecutor
import requests
from django.shortcuts import render


def _fetch_pokemon_details(pokemon):
    """Busca os detalhes de um único pokémon a partir de sua URL."""
    try:
        response = requests.get(pokemon["url"], timeout=5)
        return response.json()
    except requests.RequestException:
        return None


def _serialize_api_pokemon(details):
    if not details:
        return None

    # Formatação dos tipos e habilidades
    types = [
        {"type": {"name": item["type"]["name"]}}
        for item in details.get("types", [])
    ]

    # Tratamento seguro para extração da imagem com fallback
    sprites = details.get("sprites", {}) or {}
    other = sprites.get("other", {}) or {}
    official_artwork = other.get("official-artwork", {}) or {}

    official_art = official_artwork.get("front_default")
    front_default = sprites.get("front_default")

    image = official_art or front_default

    return {
        "id": details.get("id"),
        "name": details.get("name", ""),
        "species": details.get("species", {}).get("name", "").title(),
        "height": f"{details.get('height', 0) / 10:.1f} m",
        "weight": f"{details.get('weight', 0) / 10:.1f} kg",
        "base_experience": details.get("base_experience", 0),
        "types": types,
        "abilities": [
            item["ability"]["name"].replace("-", " ").title()
            for item in details.get("abilities", [])
        ],
        "stats": details.get("stats", []),
        "image": image,
        "official_artwork": official_art or image,
        "source": "api",
    }


def index(request):
    url = "https://pokeapi.co/api/v2/pokemon?limit=30"
    try:
        response = requests.get(url, timeout=5)
        results = response.json().get("results", [])
    except requests.RequestException:
        results = []

    # Requisições em paralelo utilizando ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:
        details_list = list(executor.map(_fetch_pokemon_details, results))

    # Serializa e remove eventuais requisições que falharam (None)
    pokemons = [
        _serialize_api_pokemon(details)
        for details in details_list
        if details is not None
    ]

    return render(request, "index.html", {"pokemon": pokemons})
