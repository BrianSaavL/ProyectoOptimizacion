from gurobipy import GRB, Model, math, quicksum

n = 5 #numero de pymes
periodos = ["enero", "febrero", "marzo", "abril",
        "mayo", "junio", "julio", "agosto",
        "septiembre", "octubre", "noviembre",
        "diciembre"]
modelo = Model()

parametros_a = {"T": 0.714, "B": 0.1066, "D": 3544000.36,
            "Vp": 29852, "Tz": 0.08, "Ka": 10*43.2,
            "Ck": 10*163000, "Qr": 1, "Yt": 378.79}

parametros_pymes = {1: {"Cr": 2747, "Cn": 4881.25, "Tn": 0.714,
                "Bn": 0.1066, "Dt": 687, "Kp": 700,
                "Lt": 0.20}, 2: {"Cr": 2747, "Cn": 4881.25, "Tn": 0.714,
                "Bn": 0.1066, "Dt": 500, "Kp": 500,
                "Lt": 0.145}, 3: {"Cr": 2747, "Cn": 4881.25, "Tn": 0.714,
                "Bn": 0.1066, "Dt": 400, "Kp": 400,
                "Lt": 0.116}, 4: {"Cr": 2747, "Cn": 4881.25, "Tn": 0.714,
                "Bn": 0.1066, "Dt": 900, "Kp": 900,
                "Lt": 0.26}, 5: {"Cr": 2747, "Cn": 4881.25, "Tn": 0.714,
                "Bn": 0.1066, "Dt": 958, "Kp": 958,
                "Lt": 0.279}}


### Analisis de sensibilidad ####
print("Ingresa el numero que corresponda para ver el modelo inicial o el analisis de sensibilidad de los parametros que consideramos importantes de discutir")
select = input("0 -> modelo inicial\n1 -> variar Tz\n2 -> variar Ck\n3 -> variar Cn\n4 -> variar Cr\n5 -> variar Kp\n")
while not select.isdigit() or int(select) not in range(0, 6):
    select = input("Ingresa un numero valido\n")
select = int(select)
if select != 0:
    direccion = input("Ingresa un numero para definir el sentido de la variación:\n1 -> aumentar el parametro\n2 -> disminuicion del parametro\n")
    while not direccion.isdigit() or int(direccion) not in range(1, 3):
        direccion = input("Ingresa un numero valido\n")
    direccion = int(direccion)
    if select == 1:
        if direccion == 1:
            parametros_a["Tz"] = parametros_a["Tz"] * 2
        else:
            parametros_a["Tz"] = parametros_a["Tz"] * 0.5
    elif select == 2:
        if direccion == 1:
            parametros_a["Ck"] = 1000000
        else:
            parametros_a["Ck"] = 3000000
    elif select == 3:
        if direccion == 1:
            for e in range(1, n+1):
                parametros_pymes[e]["Cn"] = parametros_pymes[e]["Cn"] * 2
        else:
            for e in range(1, n+1):
                parametros_pymes[e]["Cn"] = parametros_pymes[e]["Cn"] * 0.5
    elif select == 4:
        if direccion == 1:
            for e in range(1, n+1):
                parametros_pymes[e]["Cr"] = parametros_pymes[e]["Cr"] * 2
        else:
            for e in range(1, n+1):
                parametros_pymes[e]["Cr"] = parametros_pymes[e]["Cr"] * 0.5
    else:
        if direccion == 1:
            for e in range(1, n+1):
                parametros_pymes[e]["Kp"] = parametros_pymes[e]["Kp"] * 2
        else:
            for e in range(1, n+1):
                parametros_pymes[e]["Kp"] = parametros_pymes[e]["Kp"] * 0.5

##auxiliares para crear las variables que van en el diccionario ##
aux_variables_a = ["F", "R", "Tk", "Nt", "Wa", "St"]
aux_variables_binarias_a = ["X", "J"]
aux_variables_pyme = ["Ft", "Rp", "We", "Np"]
#####################################

variables_de_a = {}
variables_de_pymes = {}


for s in periodos:
    for var in aux_variables_a:
        variables_de_a[(var, s)] = modelo.addVar(vtype=GRB.CONTINUOUS, name=f"{var}_{s}")
    for var in aux_variables_binarias_a:
        variables_de_a[(var, s)] = modelo.addVar(vtype=GRB.BINARY, name=f"{var}_{s}")

for s in periodos:
    for e in range(1, n+1):
        for var in aux_variables_pyme:
            variables_de_pymes[(var, e, s)] = modelo.addVar(vtype=GRB.CONTINUOUS, name=f"{var}_{e}_{s}")

modelo.update()



##### Definicion de función objetivo#####
wa_total = [variables_de_a[i] for i in variables_de_a.keys() if "Wa" in i]
we_total = [variables_de_pymes[i] for i in variables_de_pymes.keys() if "We" in i]
np_total = list(map(lambda x: parametros_a["Qr"]*x, [variables_de_pymes[i] for i in variables_de_pymes.keys() if "Np" in i]))

total_waste = wa_total + we_total
funcion_objetivo = quicksum(total_waste) - quicksum(np_total)

modelo.setObjective(funcion_objetivo, GRB.MINIMIZE)

#### Definicion de restricciones ###########
######### R1 ##########
for s in range(1, len(periodos)):
    modelo.addConstr(
        variables_de_a[("Tk", periodos[s-1])] + variables_de_a[("R", periodos[s])] >= parametros_a["D"],
        name = f"R1_{periodos[s]}"
    )
######### R2 ##########
for s in range(1, len(periodos)):
    modelo.addConstr(
        (variables_de_a[("F", periodos[s])] + parametros_a["Tz"] * parametros_a["D"])* (parametros_a["T"] / (parametros_a["T"] + parametros_a["B"])) >= parametros_a["D"],
        name = f"R2_{s}"
    )
modelo.addConstr(
        variables_de_a[("F", periodos[0])] * (parametros_a["T"] / (parametros_a["T"] + parametros_a["B"]))  >= parametros_a["D"],
        name = f"R2_{periodos[s]}"
    )
######## R3 ##########
for s in periodos:
    modelo.addConstr(
        (variables_de_a[("Tk", s)] / parametros_a["Yt"]) <= parametros_a["Ka"] * variables_de_a[("X", s)],
        name = f"R3_{s}"
    )
####### R4 #########
M = parametros_a["D"]**10
for s in periodos:
    modelo.addConstr(
        parametros_a["Vp"] * (variables_de_a[("R", s)] + variables_de_a["St", s] - parametros_a["D"])/parametros_a["T"] >= parametros_a["Ck"] + M * (1 - variables_de_a["X", s]),
        name = f"R4A_{s}"
    )
    modelo.addConstr(
        parametros_a["Vp"] * (variables_de_a[("R", s)] + variables_de_a["St", s] - parametros_a["D"])/parametros_a["T"] <= parametros_a["Ck"] + M * variables_de_a["X", s],
        name = f"R4B_{s}"
    )
######## R5 ########
for s in range(1, len(periodos)):
    modelo.addConstr((
        variables_de_a[("R", periodos[s])] + variables_de_a[("Tk", periodos[s-1])] - parametros_a["D"] + variables_de_a[("St", periodos[s])] <= variables_de_a[("Wa", periodos[s])]),
        name = f"R5_{periodos[s]}"
    )
modelo.addConstr(
        variables_de_a[("R", periodos[0])] - parametros_a["D"] + variables_de_a[("St", periodos[0])] <= variables_de_a[("Wa", periodos[0])],
        name = f"R5_{periodos[0]}"
    )
###### R6 #########
for s in range(1, len(periodos)):
    modelo.addConstr(
        parametros_a["D"] + variables_de_a[("Tk", periodos[s])] == variables_de_a[("Tk", periodos[s-1])] + variables_de_a[("R", periodos[s])],
        name= f"R6_{periodos[s]}"
    )
###### R7 #########
modelo.addConstr(
    variables_de_a[("Tk", periodos[0])] == 0,
    name= f"R7_{periodos[0]}"
)
####### R8 ########
for s in periodos:
    for e in range(1, n+1):
        modelo.addConstr(
            variables_de_pymes[("Np", e, s)] + variables_de_pymes[("Ft", e, s)] >= parametros_pymes[e]["Dt"],
            name=f"R8_{e}_{s}"
        )
####### R9 ########
for s in periodos:
    for e in range(1, n+1):
        modelo.addConstr(
            (variables_de_pymes[("Np", e, s)] + variables_de_pymes[("Ft", e, s)] - parametros_pymes[e]["Dt"]) == variables_de_pymes[("We", e, s)],
            name=f"R9_{e}_{s}"
        )
###### R10 #########
for s in periodos:
    for e in range(1, n+1):
        modelo.addConstr(
            variables_de_pymes[("Np", e, s)] + variables_de_pymes[("Ft", e, s)] <= parametros_pymes[e]["Kp"],
            name=f"R10_{e}_{s}"
        )
####### R11 ########
for s in periodos:
    modelo.addConstr(quicksum(variables_de_pymes[("Np", e, s)] for e in range(1, n+1)) * parametros_pymes[e]["Cr"] <=
                     0.5 * parametros_pymes[e]["Cn"] * quicksum(variables_de_pymes[("Ft", e, s)] for e in range(1, n+1)),
                     name=f"R11_{s}"
                     )
######## R12 ########
for s in periodos:
    modelo.addConstr(
        quicksum(variables_de_pymes[("Np", e, s)] for e in range(1, n+1)) == variables_de_a[("Nt", s)],
                     name=f"R12_{s}"
    )
####### R13 #########
for e in range(1, n+1):
    modelo.addConstr(variables_de_pymes[("Np", e, periodos[0])] == 0,
                    name=f"R13_{e}_{s}"
                )
####### R14 ########
for s in periodos[1:]:
    modelo.addConstr(
        variables_de_a[("R", s)] ==
        (variables_de_a[("F", s)] + parametros_a["Tz"] * parametros_a["D"]) - variables_de_a[("St", s)] - variables_de_a[("Wa", s)],
        name = f"R14_{s}"
    )
modelo.addConstr(variables_de_a[("R", periodos[0])] == variables_de_a[("F", periodos[0])] * (parametros_a["T"] / (parametros_a["T"] + parametros_a["B"])) , name = f"R15_{periodos[0]}")
####### R15 ########
for s in periodos :
   modelo.addConstr(
        variables_de_a[("Nt", s)] ==
        (variables_de_a[("R", s)] + variables_de_a[("St", s)] - parametros_a["D"] - variables_de_a[("Tk", s)]),
        name = f"R15_{s}"
    )
####### R16 ########
for s in range(1, len(periodos)):
    for e in range(1, n+1):
        modelo.addConstr(
            variables_de_pymes[("Rp", e, periodos[s])] ==
            (variables_de_pymes[("Np", e, periodos[s])] + variables_de_pymes["Ft", e, periodos[s-1]]) *
            (parametros_a["T"] / (parametros_a["T"] + parametros_a["B"])),
            name = f"R16_{e}_{periodos[s]}"
        )
####### R17 #########
for s in periodos:
    for e in range(1, n+1):
        modelo.addConstr(
            variables_de_pymes[("Np", e, s)] == variables_de_a[("Nt", s)] * parametros_pymes[e]["Lt"],
            name = f"R17_{e}_{s}"
        )

modelo.update()

modelo.optimize()


modelo.printAttr("X")
modelo.write("out.sol")
#### restricciones y su holgura ####
check = input("Deseas revisar la holgura y el lado derecho de las restricciones activas\n1 -> Si\n2 -> No\n")
while not check.isdigit() or int(check) not in range(1, 3):
    check = input("Ingresa un numero valido\n")
check = int(check)
if check == 1:
    modelo.printAttr(["Sense", "Slack", "RHS"])
print("Programa terminado, gracias por tu tiempo :)")