from concurrent.futures import ThreadPoolExecutor
import requests
from django.shortcuts import render


def fetch_pokemon_detail(pokemon_data):
    response = requests.get(pokemon_data["url"])
    detalhes = response.json()

    try:
        detalhes["official_artwork"] = detalhes["sprites"]["other"][
            "official-artwork"
        ]["front_default"]
    except (KeyError, TypeError):
        detalhes["official_artwork"] = detalhes["sprites"]["front_default"]

    return detalhes


def index(request):
    url = "https://pokeapi.co/api/v2/pokemon?limit=30"
    response = requests.get(url)
    results = response.json().get("results", [])

    with ThreadPoolExecutor(max_workers=10) as executor:
        pokemons = list(executor.map(fetch_pokemon_detail, results))

    return render(request, "index.html", {"pokemon": pokemons})
