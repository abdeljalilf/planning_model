# model/constraints.py

from pyomo.environ import *

def add_constraints(model, data):
    # I, H, C, K, T = model.I, model.H, model.C, model.K, model.T
    # IHKT = model.IHKT

    # # Paramètres
    # U_ih = model.U_ih
    # lamda_k = model.lamda_k
    # eta_ih = model.eta_ih
    # Alpha_ic = model.Alpha_ic
    # Distor_ihc = model.Distor_ihc
    # D_k = model.D_k
    # BetaMin_cj = model.BetaMin_cj
    # BetaMax_cj = model.BetaMax_cj
    # Cible_cj = model.Cible_cj
    # TempsTrait_ih = model.TempsTrait_ih
    # E_k = model.E_k
    # L_k = model.L_k

    # # Variables
    # x_ihkt = model.x_ihkt
    # o_ihkt = model.o_ihkt
    # y_ihkt = model.y_ihkt
    # z_ihkt = model.z_ihkt
    # mu_ck = model.mu_ck
    # delta_ck = model.delta_ck
    
    # === (1) Satisfaction de la demande ===
    def demand_satisfaction_rule(m, k):
        return sum(
            m.eta_ih[h, i] * m.x_ihkt[i, h, k, t]
            for i, h, k2, t in m.x_ihkt.index_set()
            if k2 == k
        ) == m.D_k[k]

    model.demand_satisfaction = Constraint(model.K, rule=demand_satisfaction_rule)
    return model
  
    return model
