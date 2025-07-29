import shutil
from pyomo.environ import *

def solve_model(model, solver_name="scip", tee=False, mipgap=0.02):
    # Spécifie le chemin complet vers le binaire scip.exe
    scip_path = shutil.which("scip")
    if scip_path is None:
        scip_path = "C:/Program Files/SCIPOptSuite 9.0.1/bin/scip.exe"

    solver = SolverFactory("scip", executable=scip_path)

    # Paramètre du mipgap (SCIP accepte "limits/gap")
    solver.options["limits/gap"] = mipgap

    if not solver.available():
        raise RuntimeError(f"❌ SCIP non disponible même avec chemin : {scip_path}")

    print(f"✅ SCIP disponible. Lancement de la résolution avec gap = {mipgap}...")
    result = solver.solve(model, tee=tee)

    if result.solver.status != SolverStatus.ok and result.solver.status != SolverStatus.aborted:
        raise RuntimeError("❌ Résolution échouée.")

    print("✅ Résolution terminée.")
    return result
