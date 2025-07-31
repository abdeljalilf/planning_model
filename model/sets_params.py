# model/sets_params.py

from pyomo.environ import *

def define_sets_and_params(model, data):
    # === 1. ENSEMBLES ===
    # model.I = Set(initialize=[0,1,2,3,4,5])  # Exemple d'initialisation
    # model.J = Set(initialize=[0,1,2,3,4,5,6])  # Exemple d'initialisation
    # model.H = Set(initialize=[0,1,2,3,4])  # Exemple d'initialisation
    # model.K = Set(initialize=[1,2,3,4])  # Exemple d'initialisation
    # model.T = Set(initialize=[1,2,3,4,5,6,7,8,9,10])  # Exemple d'initialisation
    # model.T_s = Set(initialize=[0,1,2,3,4,5,6,7,8,9,10])  # Exemple d'initialisation
    
    
    # model.C = Set(initialize=[c - 1 for c in data["C_num"]])  
    model.H = Set(initialize=data["H"])
    model.I = Set(initialize=[i  for i in data["I_num"][:]])  
    model.J = Set(initialize=[j for j in data["J_num"]])  
    model.K = Set(initialize=[k  for k in data["K"][:]])  
    model.T = Set(initialize=[int(t) for t in data["T"][:]])
    model.T_s = Set(initialize=[0] + [int(t) for t in data["T"]])  
    model.C = Set(initialize=[1,2,3,4])  # Exemple d'initialisation
    
    model.S = Set(initialize=[s  for s in data["S_num"][:len(model.I)]])
    model.R = Set(initialize=[r  for r in data["R_num"]])

    model.I_names = Param(model.I, initialize=lambda m, i: data["I_names"][i - 1], within=Any)
    model.J_names = Param(model.J, initialize=lambda m, j: data["J_names"][j - 1], within=Any)
    model.H_names = Param(model.H, initialize=lambda m, h: data["H_names"][h ], within=Any)
    model.K_names = Param(model.K, initialize=lambda m, k: data["K_names"][k - 1], within=Any)
    model.R_names = Param(model.R, initialize=lambda m, r: data["R_names"][r - 1], within=Any)
    model.C_names = Param(model.C, initialize=lambda m, c: data["C_names"][c - 1], within=Any)
    model.Stock_sources = Param(model.I, initialize=lambda m, i: data["Stock_sources"][i - 1], within=Any)

    # model.S = Set(initialize=[s - 1 for s in data["S_num"]])  # Ajustement pour correspondre à l'indexation de Pyomo
    
    model.QS_mines = Set(initialize=[i  for i in data["QS_mines"]])
    model.QS_Sc1 = Set(initialize=[i  for i in data["QS_Sc1"]])
    model.QS_Sc2 = Set(initialize=[i  for i in data["QS_Sc2"]])
    model.QS_Se = Set(initialize=[i  for i in data["QS_Se"]])
    model.QSL_Sf1 = Set(initialize=[i  for i in data["QSL_Sf1"]])
    
    model.U_ih = Param(model.H, model.I, initialize=lambda m, h, i: data["U_ih"][h][i-1 ])
    model.R_ir = Param(model.R, model.I,  initialize=lambda m, r, i: data["R_ir"][r-1][ i-1])
    
    
    # === 2. PARAMÈTRES SCALAIRES ===
    model.Sigma_3 = Param(initialize=data["Sigma_3"][0])
    model.RC_tm = Param(initialize=data["RC_tm"][0])
    model.RC_if = Param(initialize=data["RC_if"][0])
    model.M_max = Param(initialize=data["M_max"][0])
    model.M_min = Param(initialize=data["M_min"][0])
    # === 3. PARAMÈTRES 1D ===
    model.Sigma_c = Param(model.C, initialize=lambda m, c: data["Sigma_c"][c-1])
    model.Sigma_h = Param(model.H, initialize=lambda m, h: data["Sigma_h"][h])
    model.D_k = Param(model.K, initialize=lambda m, k: data["D_k"][k-1 ])
    model.lamda_k = Param(model.K, initialize=lambda m, k: data["lamda_k"][k -1])
    model.E_k = Param(model.K, initialize=lambda m, k: data["E_k"][k -1])
    model.L_k = Param(model.K, initialize=lambda m, k: data["L_k"][k -1])
    model.debit_r = Param(model.R, initialize=lambda m, r: data["debit_r"][r -1])
    model.Stock_initial_i = Param(model.I, initialize=lambda m, i: data["Stock_initial_i"][i -1])

    # === 4. PARAMÈTRES 2D ===
    model.Sigma_ih = Param(model.H, model.I, initialize=lambda m, h, i: data["Sigma_ih"][h][i -1])
    model.TempsTrait_ih = Param(model.H, model.I, initialize=lambda m, h, i: data["TempsTrait_ih"][h][i -1])
    model.eta_ih = Param(model.H, model.I, initialize=lambda m, h, i: data["eta_ih"][h][i -1])
    model.Alpha_ic = Param(model.C, model.I, initialize=lambda m, c, i: data["Alpha_ic"][c-1 ][i-1 ])
    model.TauxDispo_rt = Param(model.T, model.R,  initialize=lambda m, t, r: data["TauxDispo_rt"][t-1 ][r -1])

    model.BetaMin_cj = Param(model.J, model.C, initialize=lambda m, j, c: data["BetaMin_cj"][j -1][c-1 ])
    model.BetaMax_cj = Param(model.J, model.C, initialize=lambda m, j, c: data["BetaMax_cj"][j-1 ][c-1 ])
    model.Cible_cj = Param(model.J, model.C, initialize=lambda m, j, c: data["Cible_cj"][j-1 ][c -1])

    model.Ait = Param(model.T, model.I, initialize=lambda m, t, i: data["Ait"][t-1][i -1])


    # === 5. PARAMÈTRES 3D ===
    model.Distor_ihc = Param(model.I, model.H, model.C, initialize=lambda m, i, h, c: data["Distor_ihc"][i -1][h][c -1])
    model.TempsUtilis_ihr = Param(model.I, model.H, model.R, initialize=lambda m, i, h, r: data["TempsUtilis_ihr"][i-1 ][h][r -1]) 
    
    
    model.IHKT_valid = Set(
        dimen=4,
        initialize=[
            (i, h, k, t)
            for i in model.I
            for h in model.H if model.U_ih[h, i] == 1
            for k in model.K
            for t in model.T
        ]
    )
            

    r_R2rule = model.R.at(4)  # r = 4 
    model.IHKT_for_R2_rule = Set( dimen=4, initialize=[
        (i,h,k,t)
        for i in (model.QS_mines | model.QS_Sc1 | model.QS_Sc2  | model.QSL_Sf1) & model.I
        if model.R_ir[r_R2rule, i] == 1
        for h in [0, 3, 4] if model.U_ih[h, i] == 1
        for k in model.K
        for t in model.T if t- model.TempsUtilis_ihr[i, h, r_R2rule] >=  1
        
    ]) 
    
    r_R3rule = model.R.at(5)
    model.IHKT_for_R3_rule = Set( dimen=4, initialize=[
        (i, h, k, t)
        for i in model.I if model.R_ir[r_R3rule, i] == 1
        for h in model.H if model.U_ih[h, i] == 1
        for k in model.K
        for t in model.T if t- model.TempsUtilis_ihr[i, h, r_R3rule] >=  1
    ])
    
    r_TM_rule = model.R.at(1)
    model.IHKT_for_TM_rule = Set (dimen=4, initialize= [
        (i, h, k,t)
        for i in (model.QS_mines & model.I) if model.R_ir[r_TM_rule, i] == 1
        for h in [2, 3] if model.U_ih[h, i] == 1
        for k in model.K
        for t in model.T if t- model.TempsUtilis_ihr[i, h, r_TM_rule] >=  1
        ])
                                                        
    r_IF_rule = model.R.at(2)
    model.IHKT_for_IF_rule = Set( dimen=4, initialize=[
        (i, 1, k, t)
        for i in (model.QS_mines & model.I) if model.R_ir[r_IF_rule, i] == 1 
        for h in [1] if model.U_ih[h, i] == 1
        for k in model.K
        for t in model.T if t- model.TempsUtilis_ihr[i, h, r_IF_rule] >=  1
    ])
    
    r_laverie_rule = model.R.at(3)
    model.IHKT_for_laverie_rule = Set( dimen=4, initialize=[
            (i, h, k, t)
            for i in (model.QS_mines | model.QS_Sc1 | model.QS_Sc2)& model.I
            if model.R_ir[r_laverie_rule, i] == 1
            for h in [ 3, 4] if model.U_ih[h, i] == 1
            for k in model.K
            for t in model.T if t- model.TempsUtilis_ihr[i, h, r_laverie_rule] >=  1
        ]
    )
    
    return model