# model/variables.py

from pyomo.environ import *

def define_variables(model):
    # === Variables de décision ===
    model.x_ihkt = Var(model.I, model.H, model.K, model.T, domain=NonNegativeReals)
    model.o_ihkt = Var(model.I, model.H, model.K, model.T, domain=Binary)

    # === Variables intermédiaires ===
    model.y_ihkt = Var(model.I, model.H, model.K, model.T, domain=NonNegativeReals)
    model.z_ihkt = Var(model.I, model.H, model.K, model.T, domain=NonNegativeReals)

    model.S_it = Var(model.I, model.T, domain=NonNegativeReals)

    model.mu_ck = Var(model.C, model.K, domain=NonNegativeReals)
    model.delta_ck = Var(model.C, model.K, domain=NonNegativeReals)

    return model
