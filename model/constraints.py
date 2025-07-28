# model/constraints.py

from pyomo.environ import *

def add_constraints(model, data):
    # === Déclarations locales pour clarté ===
    I, H, C, K, T = model.I, model.H, model.C, model.K, model.T

    # Paramètres requis
    U_ih       = model.U_ih
    lamda_k    = model.lamda_k
    eta_ih     = model.eta_ih
    Alpha_ic   = model.Alpha_ic
    Distor_ihc = model.Distor_ihc
    D_k        = model.D_k
    BetaMin_cj = model.BetaMin_cj
    BetaMax_cj = model.BetaMax_cj
    Cible_cj   = model.Cible_cj
    TempsUtilis_ihr = model.TempsUtilis_ihr
    debit_r    = model.debit_r
    TauxDispo_rt = model.TauxDispo_rt

    # Variables requises
    x_ihkt = model.x_ihkt
    o_ihkt = model.o_ihkt
    y_ihkt = model.y_ihkt
    z_ihkt = model.z_ihkt
    mu_ck  = model.mu_ck

    # === Constantes globales ===
    M_max = 1e5  # Grande constante
    M_min = 10   # Petite constante pour seuil mini

    # === (1) Satisfaction de la demande ===
    def demand_satisfaction_rule(m, k):
        return sum(
            eta_ih[h, i] * x_ihkt[i, h, k, t]
            for i, h, k2, t in x_ihkt.index_set() if k2 == k
        ) == D_k[k]
    model.demand_satisfaction = Constraint(K, rule=demand_satisfaction_rule)

    # === (2) Masse du composant chimique ===
    def composant_mass_rule(m, c, k):
        return mu_ck[c, k] == sum(
            eta_ih[h, i] * Alpha_ic[c, i] * Distor_ihc[i, h, c] * x_ihkt[i, h, k, t]
            for i, h, k2, t in x_ihkt.index_set() if k2 == k
        )
    model.composant_mass = Constraint(C, K, rule=composant_mass_rule)

    # === (3) Intervalle qualité exigé ===
    def quality_interval_rule(m, c, k):
        return inequality(
            BetaMin_cj[lamda_k[k], c] * D_k[k],
            mu_ck[c, k],
            BetaMax_cj[lamda_k[k], c] * D_k[k]
        )
    model.quality_interval = Constraint(C, K, rule=quality_interval_rule)

    # === (4) Unicité de la gamme utilisée pour chaque ingrédient ===
    def unicite_gamme_rule(m, i, k, t):
        return sum(
            o_ihkt[i, h, k, t]
            for h in H if (i, h, k, t) in o_ihkt
        ) <= 1
    model.unicite_gamme = Constraint(I, K, T, rule=unicite_gamme_rule)

    # === (5) Linéarisation y_ihkt & o_ihkt ===
    def yihkt_def_rule(m, i, h, k, t):
        if U_ih[h, i] == 1:
            return m.y_ihkt[i, h, k, t] == m.x_ihkt[i, h, k, t] / M_max
        else:
            return Constraint.Skip

    model.yihkt_def = Constraint(y_ihkt.index_set(), rule=yihkt_def_rule)

    def yihkt_upper_rule(m, i, h, k, t):
        if U_ih[h, i] == 1:
            return m.y_ihkt[i, h, k, t] <= m.o_ihkt[i, h, k, t]
        else:
            return Constraint.Skip

    model.yihkt_upper = Constraint(y_ihkt.index_set(), rule=yihkt_upper_rule)

    # === (6) Linéarisation z_ihkt & o_ihkt ===
    def zihkt_def_rule(m, i, h, k, t):
        if U_ih[h, i] == 1:
            return m.z_ihkt[i, h, k, t] == m.x_ihkt[i, h, k, t] / M_min
        else:
            return Constraint.Skip

    model.zihkt_def = Constraint(z_ihkt.index_set(), rule=zihkt_def_rule)

    def zihkt_lower_rule(m, i, h, k, t):
        if U_ih[h, i] == 1:
            return m.z_ihkt[i, h, k, t] >= m.o_ihkt[i, h, k, t]
        else:
            return Constraint.Skip

    model.zihkt_lower = Constraint(z_ihkt.index_set(), rule=zihkt_lower_rule)



    return model



#  # === (5) Linéarisation y_ihkt & o_ihkt ===
#     def yihkt_def_rule(m, i, h, k, t):
#         if (i, h, k, t) in y_ihkt and (i, h, k, t) in x_ihkt:
#             return y_ihkt[i, h, k, t] == x_ihkt[i, h, k, t] / M_max
#         return Constraint.Skip
#     model.yihkt_def = Constraint(y_ihkt.index_set(), rule=yihkt_def_rule)

#     def yihkt_upper_rule(m, i, h, k, t):
#         if (i, h, k, t) in y_ihkt and (i, h, k, t) in o_ihkt:
#             return y_ihkt[i, h, k, t] <= o_ihkt[i, h, k, t]
#         return Constraint.Skip
#     model.yihkt_upper = Constraint(y_ihkt.index_set(), rule=yihkt_upper_rule)

#     # === (6) Linéarisation z_ihkt & o_ihkt ===
#     def zihkt_def_rule(m, i, h, k, t):
#         if (i, h, k, t) in z_ihkt and (i, h, k, t) in x_ihkt:
#             return z_ihkt[i, h, k, t] == x_ihkt[i, h, k, t] / M_min
#         return Constraint.Skip
#     model.zihkt_def = Constraint(z_ihkt.index_set(), rule=zihkt_def_rule)

#     def zihkt_lower_rule(m, i, h, k, t):
#         if (i, h, k, t) in z_ihkt and (i, h, k, t) in o_ihkt:
#             return z_ihkt[i, h, k, t] >= o_ihkt[i, h, k, t]
#         return Constraint.Skip
#     model.zihkt_lower = Constraint(z_ihkt.index_set(), rule=zihkt_lower_rule)