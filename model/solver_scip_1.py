import shutil
from pyomo.environ import SolverFactory, SolverStatus

def solve_model(model, solver_name="scip", tee=False, mipgap=0.5):
    # 1. Chemin vers scip.exe
    scip_path = shutil.which("scip")
    if scip_path is None:
        scip_path = "C:/Program Files/SCIPOptSuite 9.0.1/bin/scip.exe"

    # 2. Initialisation du solveur
    solver = SolverFactory("scip", executable=scip_path)

    # 3. Paramètres de performance
    solver.options["limits/gap"] = mipgap                           # Écart toléré (ex: 0.1 = 10%)
    solver.options["heuristics/undercover/freq"] = -1              # Désactiver une heuristique coûteuse
    solver.options["presolving/maxrestarts"] = 2                   # Moins de redémarrages
    solver.options["presolving/maxrounds"] = 5                     # Tours de presolve limités
    solver.options["separating/maxrounds"] = 2                     # Moins de coupures
    solver.options["lp/solvefreq"] = 5                             # Éviter trop de LPs
    solver.options["branching/scorefac"] = 0.8                     # Stratégie de branchement + rapide
    solver.options["propagating/maxrounds"] = 1                    # Limite la propagation
    solver.options["presolving/emphasis"] = "aggressive"           # Presolve agressif

    # 4. Vérification disponibilité
    if not solver.available():
        raise RuntimeError(f"❌ SCIP non disponible même avec chemin : {scip_path}")

    # 5. Résolution
    print(f"✅ SCIP disponible. Lancement de la résolution avec gap = {mipgap}...")
    result = solver.solve(model, tee=tee)

    # 6. Statut
    if result.solver.status != SolverStatus.ok and result.solver.status != SolverStatus.aborted:
        raise RuntimeError("❌ Résolution échouée.")

    print("✅ Résolution terminée.")
    return result
