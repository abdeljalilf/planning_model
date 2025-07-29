import pandas as pd
import numpy as np
def get_all_data(path='data/input_data_.xlsx'):
    data = {}

    # === 1. LECTURE DE Matrix1D ===
    df1d = pd.read_excel(path, sheet_name="Matrix1D", header=None)
    for i in range(df1d.shape[0]):
        name = str(df1d.iloc[i, 0]).strip()
        values = list(df1d.iloc[i, 1:])
        values = [v for v in values if not pd.isna(v)]  #  Supprimer les nan
        data[name] = [v for v in values if pd.notna(v)]

    # === 2. LECTURE DE Matrix2D ===
    df2d = pd.read_excel(path, sheet_name="Matrix2D", header=None)

    current_name = None
    current_matrix = []
    max_cols = 0

    for i in range(df2d.shape[0]):
        first_cell = df2d.iloc[i, 0]

        if pd.notna(first_cell):  # début d'une nouvelle matrice
            # sauvegarder la précédente
            if current_name and current_matrix:
                # tronquer chaque ligne à max_cols
                trimmed = [row[:max_cols] for row in current_matrix]
                data[current_name] = trimmed
            # recommencer
            current_name = str(first_cell).strip()
            current_matrix = []
            max_cols = 0  # reset pour la nouvelle matrice

        # lire les valeurs à partir de la colonne 1
        row_vals = list(df2d.iloc[i, 1:])
        row = [val if not pd.isna(val) else 0 for val in row_vals]

        # déterminer la dernière colonne non vide
        #row_effective = [val for val in row if val != 0]
        row_effective = [val for val in row_vals if not pd.isna(val)]

        if row_effective:
            # mettre à jour le max_cols si ligne utile
            max_cols = max(max_cols, len(row_effective))
            current_matrix.append(row)

    # sauvegarder la dernière matrice
    if current_name and current_matrix:
        trimmed = [row[:max_cols] for row in current_matrix]
        data[current_name] = trimmed  

    # === 3. LECTURE DE Matrix3D ===
    df3d = pd.read_excel(path, sheet_name="Matrix3D", header=None)
    current_name = None
    current_block = []

    total_dims = {
        "I": len(data.get("I_num", [])),
        "H": len(data.get("H", [])),
        "C": len(data.get("C_num", [])),
        "J": len(data.get("J_num", [])),
        "K": len(data.get("K", [])),
        "T": len(data.get("T", [])),
        "R": len(data.get("R_num", [])),
        "S": len(data.get("S_num", []))
    }

    for i in range(df3d.shape[0]):
        first_cell = df3d.iloc[i, 0]

        if pd.notna(first_cell):  # nouvelle matrice
            # sauver la précédente
            if current_name and current_block:
                matrix_name = current_name
                # extraire indices à partir du nom (ex: D_ihc → I,H,C)
                if "_" not in matrix_name:
                    continue  # sécurité
                indices = matrix_name.split("_")[-1]  # ihc
                dim1, dim2, dim3 = indices[0].upper(), indices[1].upper(), indices[2].upper()
                n1, n2, n3 = total_dims[dim1], total_dims[dim2], total_dims[dim3]
                print(f"Saving matrix {matrix_name} with dimensions {n1}x{n2}x{n3}")
                matrix_3d = []
                for i1 in range(n1):  # premier indice = colonne
                    matrix_2d = []
                    for i2 in range(n2):  # lignes = 2e x 3e
                        row = current_block[i2 * n3:(i2 + 1) * n3]
                        matrix_2d.append([row[i3][i1] for i3 in range(n3)])
                    matrix_3d.append(matrix_2d)

                data[matrix_name] = matrix_3d

            # nouvelle matrice
            current_name = str(first_cell).strip()
            current_block = []
            values = list(df3d.iloc[i, 1:])
            row = [v if not pd.isna(v) else 0 for v in values]
            current_block.append(row)
        else:
            values = list(df3d.iloc[i, 1:])
            row = [v if not pd.isna(v) else 0 for v in values]
            current_block.append(row)

    # traitement du dernier bloc
    if current_name and current_block:
        matrix_name = current_name
        indices = matrix_name.split("_")[-1]  # ex: ihc
        dim1, dim2, dim3 = indices[0].upper(), indices[1].upper(), indices[2].upper()
        n1, n2, n3 = total_dims[dim1], total_dims[dim2], total_dims[dim3]

        matrix_3d = []
        for i1 in range(n1):
            matrix_2d = []
            for i2 in range(n2):
                row = current_block[i2 * n3:(i2 + 1) * n3]
                matrix_2d.append([row[i3][i1] for i3 in range(n3)])
            matrix_3d.append(matrix_2d)

        data[matrix_name] = matrix_3d
    # === Nettoyage : supprimer les clés vides ou 'nan' ===
    data = {
        k: v for k, v in data.items()
        if k is not None and str(k).strip().lower() != 'nan' and str(k).strip() != ''
    }
    # === Conversion automatique en np.array (matrices) ===
    for k, v in data.items():
        if isinstance(v, list) and all(isinstance(row, list) for row in v):
            data[k] = np.array(v)

    return data
