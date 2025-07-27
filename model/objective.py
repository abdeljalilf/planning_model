# model/objective.py

from pyomo.environ import *

def define_objective(model):
    def obj_rule(m):
        # Pénalité sur l'écart qualité
        term1 = sum(
            m.Sigma_c[c] * m.delta_ck[c, k]
            for c in m.C for k in m.K
        )
        # Pénalité d'utilisation des ingrédients/gammes
        term2 = sum(
            m.Sigma_ih[h, i] * m.o_ihkt[i, h, k, t]
            for i, h, k, t in m.o_ihkt.index_set()
        )
        # Coût de traitement par gamme h
        term3 = sum(
            m.Sigma_h[h] * m.x_ihkt[i, h, k, t]
            for i, h, k, t in m.x_ihkt.index_set()
        )
        # Coût d’extraction/transport
        term4 = sum(
            m.RC_tm * m.x_ihkt[i, h, k, t]  # Ajuste selon prédicat d’origine
            for i, h, k, t in m.x_ihkt.index_set()
        )
        # Total
        return term1 + term2 + term3 + term4

    model.OBJ = Objective(rule=obj_rule, sense=minimize)
    return model
