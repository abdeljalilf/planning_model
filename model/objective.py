from pyomo.environ import *

def define_objective(model, data):
    H = model.H
    I = model.I
    K = model.K
    T = model.T
    C = model.C
    J = model.J
    QS_mines = model.QS_mines

    Sigma_c = model.Sigma_c
    Sigma_h = model.Sigma_h 
    Sigma_ih = model.Sigma_ih
    Sigma_3 = model.Sigma_3 
    RC_tm = model.RC_tm
    RC_if = model.RC_if
    TempsTrait_ih = model.TempsTrait_ih
    Distor_ihc = model.Distor_ihc

    # === P1 : Pénalité qualité (écarts à la charte) ===
    def p1_rule(m):
        return sum(Sigma_c[c] * m.delta_ck[c, k] for c in C for k in K)
    
    # === P2 : Pénalité temporelle (activation oihkt) ===
    def p2_rule(m):
        return sum(
            Sigma_ih[h, i] * TempsTrait_ih[h, i] * m.o_ihkt[i, h, k, t]
            for i in I for h in H for k in K for t in T
        )

    # === P3 : Coût traitement direct ===
    def p3_rule(m):
        return sum(
            Sigma_h[h] * m.x_ihkt[i, h, k, t]
            for i in I for h in H for k in K for t in T
        )

    # === P4 : Coût extraction et transport camion ===
    def p4_rule(m):
        return sum(
            (0.5 * RC_tm * (1 if h != 1 else 0) +
             RC_if * (1 if h == 1 else 0) +
             Sigma_3) * m.x_ihkt[i, h, k, t]
            for i in QS_mines for h in H for k in K for t in T
              # pour i ∈ Extraction
        )

    model.obj = Objective(expr=p1_rule(model) + p2_rule(model) + p3_rule(model) + p4_rule(model), sense=minimize)
    return model
