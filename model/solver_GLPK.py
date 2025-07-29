# model/solver.py
from pyomo.environ import *
import shutil

def solve_model(model, solver_name="glpk", tee=False):
    glpsol_path = shutil.which("glpsol")

    if glpsol_path is None:
        # Mettre ici le chemin manuel si besoin
        glpsol_path = "C:/glpk/w64/glpsol.exe"
    solver = SolverFactory(solver_name, executable=glpsol_path)

    if not solver.available():
        raise RuntimeError(f"❌ Le solveur '{solver_name}' n'est pas disponible même avec chemin : {glpsol_path}")

    print(f"✅ Le solveur '{solver_name}' est disponible. Lancement de la résolution...")
    solver.options['mipgap'] = 0.02  # 2% de gap
    result = solver.solve(model, tee=tee)

    if result.solver.status != SolverStatus.ok and result.solver.status != SolverStatus.aborted:
        raise RuntimeError("❌ Erreur : la résolution a échoué.")

    print("✅ Résolution terminée avec succès.")
    return result
