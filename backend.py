import bpy
import numpy as np
import mathutils


def compute_barycenter(data: list) -> tuple:
    center = (0, 0, 0)

    for value in data:
        center = (center[0] + value[0], center[1] + value[1], center[2] + value[2])

    data_count = len(data)
    center = (center[0] / data_count, center[1] / data_count, center[2] / data_count)

    return center


def transform_space(axis: tuple, data: list) -> list:
    output = []

    for value in data:
        trans_value = (value[0] - axis[0], value[1] - axis[1], value[2] - axis[2])
        output.append(trans_value)

    return output


def compute_covmatrix(data: list, length: int = None) -> list:
    if length is None:
        length = len(data[0])  # nombre de coordonnées pour un point (3 car x, y et z)

    points_count = len(data)  # nombre de points dans le nuage de points

    # On trouve la moyenne en x, y et z
    average = [0 for _ in range(length)]

    for i in range(length):
        for point in data:
            average[i] += point[i]
        average[i] /= points_count

    # On initialise M : length x length (ici: 3x3)
    covMatrix = [
        [0 for _ in range(length)] for _ in range(length)
    ]

    for i in range(length):
        for j in range(length):
            for point in data:
                covMatrix[i][j] += (average[i] - point[i]) * (average[j] - point[j])
                covMatrix[i][j] /= points_count - 1

    return covMatrix


def power_method(M: list, num_simulations: int = 10) -> tuple:
    np_M = np.array(M)

    # 1) On choisit un vecteur initial
    V = np.array([0, 0, 1])
    _lambda = 0

    # 2) Pour k de 0, 1, 2 ...
    for k in range(num_simulations):
        V_normalized = V / np.linalg.norm(V)  # On normalise V

        # a) On calcule M . Vk
        M_dot_V = np_M.dot(V_normalized)

        # b) On trouve la plus grande valeur absolu de M . Vk
        _lambda = max(M_dot_V.tolist(), key=lambda x: abs(x)) 

        # c) On calcule V(k + 1)
        V = (1 / _lambda) * M_dot_V

    # 3) On retourne le k plus grand lambda et V
    return _lambda, V


def inv(point: tuple) -> tuple:
    return (-point[0], -point[1], -point[2])


def compute_bones_generation(object, members: dict) -> dict:
    principal_components = {}

    # Pour tout les membres
    for key, points_cloud in members.items():

        # ----- STEP 1 -----

        # a) On calcule le barycentre des données
        barycenter = compute_barycenter(points_cloud)
        # b) On centre les données
        center_points_cloud = transform_space(barycenter, points_cloud)  # to local space
        # c) On calcule la matrice de covariance
        covMatrix = compute_covmatrix(center_points_cloud, length=3)

        # ----- STEP 2 -----

        # d) On calcule les valeurs propres (eigenvalue), et les vecteurs propres (eigenvector)
        eigenvalue, eigenvector = power_method(covMatrix, 100)  # eigendecomposition of covariance matrix
        print(f"eigenvalue: {eigenvalue} | eigenvector: {eigenvector}")

        # ----- STEP 3 -----

        # e) On projete les données centrées sur l'eigenvector
        norm = np.linalg.norm(eigenvector)  # finding norm of the eigenvector
        proj = [
            ((np.dot(point, eigenvector) / (norm * norm)) * eigenvector).tolist() for point in center_points_cloud
        ]
        # f) On récupère les deux extrémitées
        center_pc = [
            max(proj, key=lambda x: np.linalg.norm(x)),
            min(proj, key=lambda x: np.linalg.norm(x))
        ]

        # ----- STEP 4 -----

        # g) On repositionne les deux points
        pc = transform_space(inv(barycenter), center_pc)  # to world space

        principal_components[key] = pc

    return principal_components
