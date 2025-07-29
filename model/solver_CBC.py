import shutil
from pyomo.environ import *

def solve_model(model, solver_name="cbc", tee=False, mipgap=0.02):
    cbc_path = shutil.which("cbc")
    if cbc_path is None:
        cbc_path = "C:/Cbc/bin/cbc.exe"   # Mets ici le bon chemin si besoin

    solver = SolverFactory("cbc", executable=cbc_path)
    solver.options["ratioGap"] = mipgap  # Par exemple 0.02 = 2% gap

    if not solver.available():
        raise RuntimeError(f"❌ CBC non disponible même avec chemin : {cbc_path}")

    print(f"✅ CBC disponible. Lancement de la résolution...")
    result = solver.solve(model, tee=tee)

    if result.solver.status != SolverStatus.ok and result.solver.status != SolverStatus.aborted:
        raise RuntimeError("❌ Résolution échouée.")

    print("✅ Résolution terminée.")
    return result
