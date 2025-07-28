# model/constraints.py

from pyomo.environ import *

def add_constraints(model, data):

    I, H, C, K, T = model.I, model.H, model.C, model.K, model.T
    
    # Paramètres requis
    U_ih = model.U_ih
    lamda_k = model.lamda_k
    eta_ih = model.eta_ih
    Alpha_ic = model.Alpha_ic
    Distor_ihc = model.Distor_ihc
    D_k = model.D_k
    BetaMin_cj = model.BetaMin_cj
    BetaMax_cj = model.BetaMax_cj
    Cible_cj = model.Cible_cj
    TempsUtilis_ihr = model.TempsUtilis_ihr
    debit_r = model.debit_r
    TauxDispo_rt = model.TauxDispo_rt
    # Variables requises
    x_ihkt = model.x_ihkt
    o_ihkt = model.o_ihkt
    y_ihkt = model.y_ihkt

    
    M_max = 1e5  # Grande constante, utilisée pour linéariser
    M_min = 10  # Grande constante, utilisée pour linéariser
    
    # Contrainte (1) : Satisfaction de la demande avec pertes
    def demande_avec_pertes_rule(m, k):
        return sum(eta_ih[h, i] * m.x_ihkt[i, h, k, t] for i in I for h in H for t in T) == D_k[k]
    model.DemandeAvecPertes = Constraint(K, rule=demande_avec_pertes_rule)
    
    # === Contrainte (2) : Calcul du poids chimique mu_ck
    def mu_ck_rule(m, c, k):
        return m.mu_ck[c, k] == sum(
            eta_ih[h, i] * Alpha_ic[c, i] * Distor_ihc[i, h, c] * m.x_ihkt[i, h, k, t]
            for i in I for h in H for t in T
        )
    model.MasseChimique = Constraint(C, K, rule=mu_ck_rule)

    # === Contrainte (3) : Intervalle de qualité autorisé
    def qualite_cible_rule(m, c, k):
        return inequality(
            BetaMin_cj[lamda_k[k], c] * D_k[k],
            m.mu_ck[c, k],
            BetaMax_cj[lamda_k[k], c] * D_k[k]
        )
    model.IntervalleQualite = Constraint(C, K, rule=qualite_cible_rule)

    # === (4) : chaque ingrédient passe par au plus une gamme par période et commande
    def mono_gamme_rule(m, i, k, t):
        return sum(m.o_ihkt[i, h, k, t] for h in m.H if U_ih[h, i] == 1) <= 1
    model.MonoGamme = Constraint(model.I, model.K, model.T, rule=mono_gamme_rule)

    # === (5) : définition de y_ihkt pour borne max
    def y_upper_rule(m, i, h, k, t):
        return m.y_ihkt[i, h, k, t] <= m.o_ihkt[i, h, k, t]
    model.LiaisonY = Constraint(I, H, K, T, rule=y_upper_rule)

    def y_def_rule(m, i, h, k, t):
        return m.y_ihkt[i, h, k, t] == m.x_ihkt[i, h, k, t] / M_max
    model.DefinitionY = Constraint(I, H, K, T, rule=y_def_rule)

    # === (6) : définition de z_ihkt pour borne min
    def z_lower_rule(m, i, h, k, t):
        return m.z_ihkt[i, h, k, t] >= m.o_ihkt[i, h, k, t]
    model.LiaisonZ = Constraint(I, H, K, T, rule=z_lower_rule)

    def z_def_rule(m, i, h, k, t):
        return m.z_ihkt[i, h, k, t] == m.x_ihkt[i, h, k, t] / M_min
    model.DefinitionZ = Constraint(I, H, K, T, rule=z_def_rule)
    
    # === (7) : intervalle de temps de livraison
    # borne inférieure : E_k * o_ihkt ≤ (t + TempsTrait_ih) * o_ihkt
    def fenetre_livraison_inf_rule(m, i, h, k, t):
        return m.E_k[k] * m.o_ihkt[i, h, k, t] <= (t + m.TempsTrait_ih[h, i]) * m.o_ihkt[i, h, k, t]
    model.FenetreLivraison_inf = Constraint( I, H, K, T, rule=fenetre_livraison_inf_rule)
    # borne supérieure : (t + TempsTrait_ih) * o_ihkt ≤ L_k * o_ihkt
    def fenetre_livraison_sup_rule(m, i, h, k, t):
        return (t + m.TempsTrait_ih[h, i]) * m.o_ihkt[i, h, k, t] <= m.L_k[k] * m.o_ihkt[i, h, k, t]
    model.FenetreLivraison_sup = Constraint(I, H, K, T, rule=fenetre_livraison_sup_rule)
    
    # === (8) Capacité R2 (r = 4) pour h ∈ {0, 3, 4}
    def capacite_R2_rule(m, t):
        r = m.R.at(4)  # r = 4 
        return inequality (sum(
            m.eta_ih[h, i] *  x_ihkt[i, h, k, int(t - TempsUtilis_ihr[i, h, r])] 
            for i in m.I for h in H for k in K
            if U_ih[h, i] == 1 and int(t - TempsUtilis_ihr[i, h, r]) >= 1 and h in [0, 3, 4]
        ) , debit_r[r] * TauxDispo_rt[t, r])
    model.CapaciteR2 = Constraint(T, rule=capacite_R2_rule)

    # # === (9) Capacité R3 (r = 5), tout h admissible
    def capacite_R3_rule(m, t):
        r = m.R.at(5)  # r = 5
        return inequality( sum(
            m.eta_ih[h, i] * x_ihkt[i, h, k, int(t - TempsUtilis_ihr[i, h, r])]
            for i in m.I for h in H for k in K
            if U_ih[h, i] == 1 and int(t - TempsUtilis_ihr[i, h, r]) >= 1
        ) , debit_r[r] * TauxDispo_rt[t, r])
    model.CapaciteR3 = Constraint(T, rule=capacite_R3_rule)

    # === (10) Capacité TM (r = 1), h ∈ {2,3}
    def capacite_TM_rule(m, t):
        r = m.R.at(1)  # r = 1
        return inequality( sum(
            x_ihkt[i, h, k, int(t - TempsUtilis_ihr[i, h, r])]
            for i in I for h in H for k in K
            if U_ih[h, i] == 1 and int(t - TempsUtilis_ihr[i, h, r]) >= 1 and h in [2, 3]
        ),  debit_r[r] * TauxDispo_rt[t, r])
    model.CapaciteTM = Constraint(T, rule=capacite_TM_rule)

    # === (11) Capacité IF (r = 2), h = 1
    def capacite_IF_rule(m, t):
        r = m.R.at(2)  # r = 2
        return inequality(sum(
            x_ihkt[i, h, k, int(t - TempsUtilis_ihr[i, h, r])]
            for i in I for h in H for k in K
            if U_ih[h, i] == 1 and int(t - TempsUtilis_ihr[i, h, r]) >= 1 and h == 1
        ), debit_r[r] * TauxDispo_rt[t, r])
    model.CapaciteIF = Constraint(T, rule=capacite_IF_rule)

    # === (12) Capacité Laverie (r = 3), h ∈ {3, 4}
    def capacite_laverie_rule(m, t):
        r = m.R.at(3)  # r = 3
        return inequality( sum(
            x_ihkt[i, h, k, int(t - TempsUtilis_ihr[i, h, r])]
            for i in m.I for h in m.H for k in m.K
            if U_ih[h, i] == 1 and int(t - TempsUtilis_ihr[i, h, r]) >= 1 and h in [3, 4]
        ) , debit_r[r] * TauxDispo_rt[t, r])
    model.CapaciteLaverie = Constraint(T, rule=capacite_laverie_rule)
    
    # === (13) Initialisation du stock
    def init_stock_rule(m, i):
        return m.S_it[i, 0] == m.Stock_initial_i[i]
    model.InitStock = Constraint(I, rule=init_stock_rule)

    # === (14) QS_mines : stock augmente par Ait, puis consommé
    def stock_mines_rule(m, i, t):
        if t == 0:
            return Constraint.Skip
        return m.S_it[i, t] == m.S_it[i, t - 1] + m.Ait[t, i] - sum(
            m.x_ihkt[i, h, k, t] for h in m.H if m.U_ih[h, i] == 1 for k in m.K
        )
    model.StockQSmines = Constraint(model.QS_mines, model.T, rule=stock_mines_rule)

    # === (15) QS_Sc2 : stock diminue pour h=4
    def stock_Sc2_rule(m, i, t):
        if t == 0:
            return Constraint.Skip
        return m.S_it[i, t] == m.S_it[i, t - 1] - sum(
            m.x_ihkt[i, h, k, t] for h in m.H if m.U_ih[h, i] == 1 and h == 4 for k in m.K
        )
    model.StockQSc2 = Constraint(model.QS_Sc2, model.T, rule=stock_Sc2_rule)

    # === (16) QS_Sc1 : stock diminue pour h = 0 ou h = 4
    def stock_Sc1_rule(m, i, t):
        if t == 0:
            return Constraint.Skip
        return m.S_it[i, t] == m.S_it[i, t - 1] - sum(
            m.x_ihkt[i, h, k, t] for h in m.H if m.U_ih[h, i] == 1 and h in [0, 4] for k in m.K
        )
    model.StockQSc1 = Constraint(model.QS_Sc1, model.T, rule=stock_Sc1_rule)

    # === (17) QS_Se : stock diminue pour h = 0
    def stock_Se_rule(m, i, t):
        if t == 0:
            return Constraint.Skip
        return m.S_it[i, t] == m.S_it[i, t - 1] - sum(
            m.x_ihkt[i, h, k, t] for h in m.H if m.U_ih[h, i] == 1 and h == 0 for k in m.K
        )
    model.StockQSe = Constraint(model.QS_Se, model.T, rule=stock_Se_rule)

    # === (18) QSL_Sf1 : stock diminue pour h = 0
    def stock_Sf1_rule(m, i, t):
        if t == 0:
            return Constraint.Skip
        return m.S_it[i, t] == m.S_it[i, t - 1] - sum(
            m.x_ihkt[i, h, k, t] for h in m.H if m.U_ih[h, i] == 1 and h == 0 for k in m.K
        )
    model.StockQSLsf1 = Constraint(model.QSL_Sf1, model.T, rule=stock_Sf1_rule)

    # === (19)  : stock positif
    def stock_positif_rule(m, i, t):
        return m.S_it[i, t] >= 0
    model.StockPositif = Constraint(model.I, model.T, rule=stock_positif_rule)

    
    # === Contrainte (20) : Calcul de delta_ck selon la distance à la cible
    def delta_ck_inf_rule(m, c, k):
        return m.delta_ck[c, k] >= m.mu_ck[c, k] - D_k[k] * Cible_cj[lamda_k[k], c]

    def delta_ck_sup_rule(m, c, k):
        return m.delta_ck[c, k] <= D_k[k] * Cible_cj[lamda_k[k], c] - m.mu_ck[c, k]

    model.DeltaInf = Constraint(C, K, rule=delta_ck_inf_rule)
    model.DeltaSup = Constraint(C, K, rule=delta_ck_sup_rule)

    return model
