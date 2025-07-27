from data.input_data import get_all_data
from pyomo.environ import *
from model.sets_params import define_sets_and_params
from model.variables import define_variables
from model.objective import define_objective
from model.solver import solve_model
from model.constraints import add_constraints
from pyomo.util.infeasible import log_infeasible_constraints
import logging
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.WARNING)


def main():
    data = get_all_data()
    data = get_all_data()
    model = ConcreteModel()
    model = define_sets_and_params(model, data)
    define_variables(model)          #  les variables d’abord
    model = add_constraints(model, data)  # ensuite les contraintes
    define_objective(model, data)
    
    # Résoudre
    #result = solve_model(model, solver_name="cbc")  # ou "glpk"
    result = solve_model(model, solver_name="glpk",tee=True)
    model.write('modele.lp', io_options={'symbolic_solver_labels': True})
    # Afficher les contraintes non satisfaites
    print("🔍 Diagnostic d’inféasibilité :")
    log_infeasible_constraints(model, log_expression=True, log_variables=True)
    

    print("🔍 Valeur de la fonction objectif =", value(model.obj))
    
    #print("🔍 Valeur de la fonction objectif =", value(model.obj))



if __name__ == "__main__":
    main()
