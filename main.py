# main.py

from data.input_data import get_all_data
from pyomo.environ import *
from model.sets_params import define_sets_and_params
from model.variables import define_variables
from model.objective import define_objective
from model.solver_GLPK import solve_model
from model.solver_CBC import solve_model
from model.constraints import add_constraints
from model.constraints_copy import add_constraints
from pyomo.util.infeasible import log_infeasible_constraints
import logging
logging.basicConfig(level=logging.INFO)

def main():
    # 1. Chargement des données
    data = get_all_data()
    # 2. Création du modèle Pyomo
    model = ConcreteModel()
    model = define_sets_and_params(model, data)
    define_variables(model)
    model = add_constraints(model, data)  # ou juste add_constraints(model, data)
    define_objective(model)
    
    # 3. Affichage des informations du modèle
    num_vars = sum(1 for v in model.component_objects(Var, active=True) for _ in v)
    num_constraints = sum(1 for c in model.component_objects(Constraint, active=True) for _ in c)

    print(f"Nombre total de variables     : {num_vars}")
    print(f"Nombre total de contraintes  : {num_constraints}")

    # Variables binaires
    num_bin_vars = sum(1 for v in model.component_objects(Var, active=True)
                    for index in v if v[index].domain == Binary)
    print(f"Nombre de variables binaires : {num_bin_vars}")

    # Variables continues
    num_cont_vars = sum(1 for v in model.component_objects(Var, active=True)
                        for index in v if v[index].domain == NonNegativeReals)
    print(f"Nombre de variables continues: {num_cont_vars}")


    # 3. Résolution
    result = solve_model(model, tee=True)
    model.write('modele.lp', io_options={'symbolic_solver_labels': True})

     
    print("\n------ QUALITÉ DES COMPOSANTS (ratio) ---------")       
    for c in model.C:
        for k in list(model.K)[:2]:
            mu = model.mu_ck[c, k].value or 0
            D = model.D_k[k]
            ratio = mu / D if D > 0 else 0
            j = model.lamda_k[k]
            bmin = model.BetaMin_cj[j, c]
            bmax = model.BetaMax_cj[j, c]
            print(f"c={c}, k={k}: ratio={ratio:.4f}  [{bmin}, {bmax}]")


    # 5. Affichage valeur fonction objectif
    try:
        print("🔍 Valeur de la fonction objectif =", value(model.OBJ))
    except Exception as e:
        print("⚠️ Erreur lors de l’évaluation de la fonction objectif :", e)

if __name__ == "__main__":
    main()
