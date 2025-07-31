# model/afichage.py
import pandas as pd
from pyomo.environ import *
import pandas as pd
import dataframe_image as dfi

def extract_blending_results(model):
    # Récupération des noms (labels)
    i_names = model.I_names
    h_names = model.H_names
    k_names = model.K_names
    j_names = model.J_names
    stock_sources = model.Stock_sources
    E_k = model.E_k
    L_k = model.L_k
    commande= model.D_k
    num_commandes = model.K

    # Pour retrouver la qualité demandée pour chaque commande k
    # lamda_k est l'indice du produit QM associé à la commande k
    get_qm = lambda k: j_names[model.lamda_k[k]]

    results = []
    for (i, h, k, t) in model.x_ihkt:
        val = model.x_ihkt[i, h, k, t].value
        real_val = val* model.eta_ih[h, i]
        binary_val = model.o_ihkt[i, h, k, t].value
        if val is not None and val > 1e-3:
            results.append({
                "N°":num_commandes.at(k),
                "Commande": k_names[k],
                "Qualité demandée (QM)": get_qm(k),
                "Nom ingrédient": i_names[i],
                "Stock source": stock_sources[i],
                "Gamme": f"{h_names[h]} ({h}) ",
                "t": t ,
                "x_ihkt (tonnes)": val,
                "Real_X_ihkt": real_val ,  # Conversion en tonnes
                # "o_ihkt (binaire)": binary_val,
                "E_k": E_k[k],
                "L_k": L_k[k],
                "Quantity commande": commande[k]
            })
    df = pd.DataFrame(results)
    # Ajout du % blending
    df['Total_commande'] = df.groupby('Commande')['Real_X_ihkt'].transform('sum')
    df['%_blending'] = (df['x_ihkt (tonnes)'] / df['Total_commande']) * 100
    df.sort_values(by=['N°', 't', 'x_ihkt (tonnes)'], ascending=[True, True, False], inplace=True)
    return df

def save_blending_results_to_csv(df, filename='blending_results_table15.csv'):
    df.to_csv(filename, index=False)
    print(f"✅ Résultats enregistrés dans {filename}")

# def export_tableau_15_par_commande(df, export_excel=False):
#     import pandas as pd

#     if export_excel:
#         with pd.ExcelWriter('resultats_tableau_15_par_commande.xlsx') as writer:
#             for cmd in df['Commande'].unique():
#                 df_cmd = df[df['Commande'] == cmd][[
#                     'Qualité demandée (QM)', 'Nom ingrédient', 'Stock source', 'Gamme', 't', 'x_ihkt (tonnes)', '%_blending'
#                 ]].sort_values('x_ihkt (tonnes)', ascending=False)
#                 df_cmd.to_excel(writer, sheet_name=f"{cmd}", index=False)
#         print("✅ Exporté dans 'resultats_tableau_15_par_commande.xlsx' (une feuille par commande)")

#     # Affichage console (markdown-friendly)
#     for cmd in df['Commande'].unique():
#         print(f"\n### 🟢 Commande : **{cmd}** | QM demandée : **{df[df['Commande']==cmd]['Qualité demandée (QM)'].iloc[0]}**\n")
#         display_df = df[df['Commande'] == cmd][[
#             'Nom ingrédient', 'Stock source', 'Gamme', 't', 'x_ihkt (tonnes)', '%_blending'
#         ]].sort_values('x_ihkt (tonnes)', ascending=False)
#         print(display_df.to_markdown(index=False, floatfmt=".2f"))
#         print(f"\nTotal livré : {display_df['x_ihkt (tonnes)'].sum():,.2f} t")


def export_fusion_style_table(df, filename="S_blending_table.png"):
    # Colonnes à garder (dans l'ordre)
    # cols = [
    #     'Commande', 'Qualité demandée (QM)', 'Nom ingrédient',
    #     'Stock source', 'Gamme', 't',
    #     'x_ihkt (tonnes)', 'Total_commande', '%_blending'
    # ]
    cols = df.columns.tolist()
    df = df[cols].copy()

    # Trier par numéro de commande (extraire le n° si présent)
    df['Commande_num'] = df['Commande'].str.extract(r'(\d+)').astype(float)
    df = df.sort_values(by=['Commande_num', 't'])
    df = df.drop(columns='Commande_num')

    # Masquer les doublons dans la colonne 'Commande'
    df['Commande'] = df['Commande'].where(~df['Commande'].duplicated(), "")

    # Format des colonnes numériques
    df['x_ihkt (tonnes)'] = df['x_ihkt (tonnes)'].round(2)
    df['Total_commande'] = df['Total_commande'].round(2)
    df['%_blending'] = df['%_blending'].map(lambda x: f"{x:.2f}%")

    # Création du style avec table sans index
    styled = (
        df.style
        .hide(axis="index")  
        .set_table_styles([
            {"selector": "thead th", "props": [("font-weight", "bold"), ("background-color", "#f0f0f0"), ("border", "1px solid black")]},
            {"selector": "td", "props": [("text-align", "center"), ("border", "1px solid black"), ("padding", "6px")]}
        ])
    )

    # Exporter en image (en mode matplotlib pour compatibilité Jupyter)
    dfi.export(styled, filename, table_conversion="matplotlib")
    print(f"✅ Tableau exporté dans : {filename}")

import pandas as pd

def extract_tenurs_results(model):
    # Récupération des noms (labels)
    k_names = model.K_names
    j_names = model.J_names
    commande = model.D_k
    num_commandes = model.K
    C_names = model.C_names

    # Pour retrouver la qualité demandée pour chaque commande k
    get_qm = lambda k: j_names[model.lamda_k[k]]

    results = []
    for k in num_commandes:
        j = model.lamda_k[k]
        result_entry = {
            "Commande": k_names[k],
            "Qualité demandée (QM)": get_qm(k),
            "mu_ck": sum(model.mu_ck[c, k].value for c in model.C),
            "D_k": commande[k],
        }

        for c in model.C:
            result_entry[f"Cible_{C_names[c]}"] = model.Cible_cj[j, c]
            result_entry[f"Teneur_{C_names[c]}"] = model.mu_ck[c, k].value / commande[k]
        

        # Ajout du résultat à la liste
        results.append(result_entry)

    # Création du DataFrame
    df = pd.DataFrame(results)
    return df

def Stocks_utilisation(model):
    data = []
    I_names = model.I_names
    for i in model.I:
        initial = model.Stock_initial_i[i]
        extrait = sum(
            model.x_ihkt[i, h, k, t].value
            for h in model.H
            for k in model.K
            for t in model.T
            if (i, h, k, t) in model.IHKT_valid
        )
        final = model.S_it[i, model.T.last()].value
        ajout = sum(model.Ait[t, i] for t in model.T)
        flux_total = initial  - extrait

        data.append({
            "Ingrédient": f"{I_names[i]} ({i})",
            "Stock initial": initial,
            "Extrait total": extrait,
            "Ajout total": ajout,
            "Flux Sortant": flux_total,
            "Flux Entrant": ajout,
            "Stock final": final
        })

    df = pd.DataFrame(data)
    df = df.round(2)
    return df

def compute_resource_utilization(model, data):
    # Récupère les ensembles/noms
    R = list(model.R)
    T = list(model.T)
    R_names = data["R_names"] if "R_names" in data else {r: str(r) for r in R}

    # Résultat stocké dans une liste de dictionnaires
    results = []

    # Mapping des ensembles de flux associés à chaque ressource (à adapter si besoin !)
    resource_sets = {
        1: model.IHKT_for_TM_rule,      # TM
        2: model.IHKT_for_IF_rule,      # IF
        3: model.IHKT_for_laverie_rule, # Laverie
        4: model.IHKT_for_R2_rule,      # R2
        5: model.IHKT_for_R3_rule,      # R3
    }

    # Coefficient multiplicatif éventuel (eta_ih) pour chaque ressource
    # (adapté si tu l’utilises dans la contrainte de capacité correspondante)
    use_eta = {1: False, 2: False, 3: False, 4: True, 5: True}

    for r in R:
        for t in T:
            if r not in resource_sets:
                continue  # ignore si pas défini
            ihkt_set = resource_sets[r]
            if use_eta[r]:
                flux = sum(float(model.eta_ih[h, i]) * model.x_ihkt[i, h, k, t].value
                           for (i, h, k, t2) in ihkt_set if t2 == t
                           if model.x_ihkt[i, h, k, t].value is not None)
            else:
                flux = sum(model.x_ihkt[i, h, k, t].value
                           for (i, h, k, t2) in ihkt_set if t2 == t
                           if model.x_ihkt[i, h, k, t].value is not None)
            cap = float(model.debit_r[r]) * float(model.TauxDispo_rt[t, r])
            taux = flux / cap if cap > 1e-8 else None
            results.append({
                "Période": t,
                "Ressource": R_names[r] if r in R_names else r,
                "Flux_total": flux,
                "Capacité": cap,
                "Taux_utilisation": taux
            })

    df_util = pd.DataFrame(results)
    df_util=df_util.sort_values(by=['Période','Ressource' ], ascending=[True, True])
    df_util = df_util.reset_index(drop=True)
    return df_util
