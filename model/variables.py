# model/variables.py

from pyomo.environ import *

def define_variables(model):
    # Variables de décision principales
    model.x_ihkt = Var(
        ((i, h, k, t)
         for k in model.K
         for t in model.T
         for i in model.I
         for h in model.H
         if model.U_ih[h, i] == 1),  # Prédicat 1 : compatibilité ingrédient-gamme
        domain=NonNegativeIntegers
    )
    model.o_ihkt = Var(
        ((i, h, k, t)
         for k in model.K
         for t in model.T
         for i in model.I
         for h in model.H
         if model.U_ih[h, i] == 1),
        domain=Binary
    )
    # Variables intermédiaires
    model.y_ihkt = Var(
        ((i, h, k, t)
         for k in model.K
         for t in model.T
         for i in model.I
         for h in model.H
         if model.U_ih[h, i] == 1),
        domain=NonNegativeReals
    )
    model.z_ihkt = Var(
        ((i, h, k, t)
         for k in model.K
         for t in model.T
         for i in model.I
         for h in model.H
         if model.U_ih[h, i] == 1),
        domain=NonNegativeReals
    )

    model.S_it = Var(model.I, model.T, domain=NonNegativeIntegers)
    model.mu_ck = Var(model.C, model.K, domain=NonNegativeReals)
    model.delta_ck = Var(model.C, model.K, domain=NonNegativeReals)
    return model
