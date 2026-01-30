import os

cwd = os.getcwd()
path = os.path.join(cwd, "configs")
os.makedirs(path, exist_ok=True)

hidden_units = [2**i for i in range(1, 10)]
layers = [1, 2, 3]
DoF = 3

for l in layers:
    for h in hidden_units:

        if l == 1 and h < 128:
            continue  # skip small networks with 1 hidden layer to reduce number of experiments
        elif l == 2 and h < 16:
            continue  # skip small networks with 2 hidden layers to reduce number of experiments

        layers_no_processed = [DoF] + [h] * l + [1]
        layers = str(layers_no_processed).replace(" ", "")
        name = "_".join([str(h)] * l)
        with open(f"{path}/{DoF}_{name}.txt", "w") as f:
            f.write(f"experiment.name={DoF}d_{name}_hidden\n")
            f.write(f"model.architecture={layers}\n")
