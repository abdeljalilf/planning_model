# main.py

from data.input_data import get_all_data
from pyomo.environ import *
from model.sets_params import define_sets_and_params
from model.variables import define_variables
from model.objective import define_objective
from model.solver import solve_model
from model.constraints import add_constraints
from pyomo.util.infeasible import log_infeasible_constraints

def main():
    # 1. Chargement des données
    data = get_all_data()
    # 2. Création du modèle Pyomo
    model = ConcreteModel()
    model = define_sets_and_params(model, data)
    define_variables(model)
    model = add_constraints(model, data)  # ou juste add_constraints(model, data)
    define_objective(model)
    
    # 3. Résolution
    result = solve_model(model, solver_name="glpk", tee=True)
    model.write('modele.lp', io_options={'symbolic_solver_labels': True})

    # 4. Diagnostic d'inféasibilité (utile pour debug)
    print("🔍 Diagnostic d’inféasibilité :")
    log_infeasible_constraints(model, log_expression=True, log_variables=True)
    for k in model.K:
        lhs = sum(model.eta_ih[h, i] * model.x_ihkt[i, h, k, t].value
                for i, h, k2, t in model.x_ihkt.index_set() if k2 == k)
        print(f"Satisfaction de la demande pour k={k}: lhs={lhs}, D_k={model.D_k[k]}")

    # 5. Affichage valeur fonction objectif
    try:
        print("🔍 Valeur de la fonction objectif =", value(model.OBJ))
    except Exception as e:
        print("⚠️ Erreur lors de l’évaluation de la fonction objectif :", e)

if __name__ == "__main__":
    main()
