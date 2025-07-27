# model/afichage.py
def afficher_resultats(model):
    print("\n===== Résultats principaux =====")

    print("\n--- Quantités x_ihkt ---")
    for i in model.I:
        for h in model.H:
            for k in model.K:
                for t in model.T:
                    val = model.x_ihkt[i, h, k, t].value
                    if val is not None and val > 1e-4:
                        print(f"x_ihkt[{i},{h},{k},{t}] = {val:.2f}")

    print("\n--- Stocks S_it ---")
    for i in model.I:
        for t in model.T:
            val = model.S_it[i, t].value
            if val is not None and val > 1e-4:
                print(f"S_it[{i},{t}] = {val:.2f}")

    print("\n--- Masse chimique mu_ck ---")
    for c in model.C:
        for k in model.K:
            val = model.mu_ck[c, k].value
            if val is not None and val > 1e-4:
                print(f"mu_ck[{c},{k}] = {val:.2f}")

    print("\n--- Deltas (écarts) delta_ck ---")
    for c in model.C:
        for k in model.K:
            val = model.delta_ck[c, k].value
            if val is not None and val > 1e-4:
                print(f"delta_ck[{c},{k}] = {val:.2f}")

    print("\n--- Variables binaires o_ihkt activées ---")
    for i in model.I:
        for h in model.H:
            for k in model.K:
                for t in model.T:
                    val = model.o_ihkt[i, h, k, t].value
                    if val is not None and round(val) == 1:
                        print(f"o_ihkt[{i},{h},{k},{t}] = 1")
