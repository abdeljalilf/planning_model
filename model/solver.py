from pyomo.environ import *
import shutil

def solve_model(model, solver_name="glpk",tee=False):
    glpsol_path = shutil.which("glpsol")
    # print("🔍 Chemin détecté pour glpsol :", glpsol_path)

    if glpsol_path is None:
        # forcer le chemin ici si non détecté automatiquement
        glpsol_path = "C:/glpk/w64/glpsol.exe"

    solver = SolverFactory(solver_name, executable=glpsol_path)

    if not solver.available():
        raise RuntimeError(f"❌ Le solveur '{solver_name}' n'est pas disponible même avec chemin : {glpsol_path}")

    # print(f"✅ Le solveur '{solver_name}' est disponible. Lancement de la résolution...")
    result = solver.solve(model, tee=tee)

    if result.solver.status != SolverStatus.ok:
        raise RuntimeError("❌ Erreur : la résolution a échoué.")

    print("✅ Résolution terminée avec succès.")
    return result
