import json
import os
from pyomo.environ import value

def clean(val):
    return max(0.0, round(val, 4)) if val is not None else 0.0

def save_solution(model, filepath='outputs/solution.json'):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    solution = {
        "objective": value(model.OBJ),
        "x_ihkt": {},
        "o_ihkt": {},
        "S_it": {},
        "mu_ck": {},
        "delta_ck": {}
    }

    for (i, h, k, t) in model.IHKT_valid:
        val = clean(model.x_ihkt[i, h, k, t].value)
        if val is not None:
            solution["x_ihkt"][f"{i},{h},{k},{t}"] = val

        oval = model.o_ihkt[i, h, k, t].value
        if oval is not None:
            solution["o_ihkt"][f"{i},{h},{k},{t}"] = round(oval)

    for i in model.I:
        for t in model.T:
            val = clean(model.S_it[i, t].value)
            if val is not None:
                solution["S_it"][f"{i},{t}"] = val

    for c in model.C:
        for k in model.K:
            val = clean(model.mu_ck[c, k].value)
            delta = clean(model.delta_ck[c, k].value)
            if val is not None:
                solution["mu_ck"][f"{c},{k}"] = val
            if delta is not None:
                solution["delta_ck"][f"{c},{k}"] = delta

    with open(filepath, "w") as f:
        json.dump(solution, f, indent=2)

    print(f"✅ Solution sauvegardée dans {filepath}")


def load_solution_into_model(model, filepath='outputs/solution.json'):
    with open(filepath) as f:
        solution = json.load(f)

    for key, val in solution["x_ihkt"].items():
        i, h, k, t = map(int, key.split(","))
        model.x_ihkt[i, h, k, t].set_value(val)

    for key, val in solution["o_ihkt"].items():
        i, h, k, t = map(int, key.split(","))
        model.o_ihkt[i, h, k, t].set_value(val)

    for key, val in solution["S_it"].items():
        i, t = map(int, key.split(","))
        model.S_it[i, t].set_value(val)

    for key, val in solution["mu_ck"].items():
        c, k = map(int, key.split(","))
        model.mu_ck[c, k].set_value(val)

    for key, val in solution["delta_ck"].items():
        c, k = map(int, key.split(","))
        model.delta_ck[c, k].set_value(val)

    print("✅ Solution réinjectée dans le modèle Pyomo")
    print(" Valeur de la fonction objectif :", solution["objective"])
