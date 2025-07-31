import shutil
from pyomo.environ import *
from pyomo.core import Var

# Profil "fort" : présolve/coupes agressives, meilleur relâchement, plus coûteux en temps
STRONG = {
    "limits/gap": 0.01,          # sera éventuellement écrasé par l'argument mipgap
    "parallel/maxnthreads": -1,
    "presolving/maxrounds": 20,
    "separating/maxroundsroot": 20,
    "branching/preferbinary": True,
    "cuts/rootonly": False,
    "heuristics/emphasis": "aggressive",
    # pas de limits/time selon ta contrainte
}

def _apply_warm_start_binary_zeros(model):
    """Warm start simple : initialise toutes les variables binaires à 0 si non initialisées."""
    for comp in model.component_objects(Var, active=True):
        is_binary = False
        try:
            is_binary = comp.is_binary()
        except Exception:
            pass
        if not is_binary:
            try:
                for idx in comp:
                    vd = comp[idx]
                    lb = value(vd.lb) if vd.lb is not None else None
                    ub = value(vd.ub) if vd.ub is not None else None
                    if lb == 0 and ub == 1 and vd.domain is Binary:
                        is_binary = True
                        break
            except Exception:
                pass
        if is_binary:
            for idx in comp:
                if comp[idx].value is None:
                    comp[idx].value = 0

def solve_model(model, solver_name="scip", tee=False, mipgap=0.005, warm_start=True):
    """
    Résout le modèle avec SCIP profil STRONG.
    - mipgap : gap cible (écrase STRONG['limits/gap'] si fourni)
    - warm_start : si True, initialise toutes les binaires à 0 (si non déjà initialisées)
    """
    if warm_start:
        _apply_warm_start_binary_zeros(model)

    scip_path = shutil.which("scip")
    if scip_path is None:
        scip_path = "C:/ Program Files/SCIPOptSuite 9.0.1/bin/scip.exe"

    solver = SolverFactory("scip", executable=scip_path)

    # Charger le profil STRONG
    solver.options.update(STRONG)

    # Priorité à l'argument mipgap si différent de None
    if mipgap is not None:
        solver.options["limits/gap"] = float(mipgap)

    if not solver.available():
        raise RuntimeError(f"❌ SCIP non disponible même avec chemin : {scip_path}")

    print(f"✅ SCIP (STRONG) disponible. Lancement avec gap cible = {solver.options['limits/gap']} ...")
    results = solver.solve(model, tee=tee)

    if results.solver.status not in (SolverStatus.ok, SolverStatus.aborted):
        raise RuntimeError("❌ Résolution échouée.")

    print("✅ Résolution terminée (profil STRONG).")
    return results
