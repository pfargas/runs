import os
import matplotlib.pyplot as plt

RESULTS_DIR = "out/"
DoF = 3


def ensure_dir(dir):

    # check that it is an absolute path
    if not os.path.isabs(dir):
        dir = os.path.join(os.getcwd(), dir)

    # check that the directory exists
    if not os.path.exists(dir):
        raise FileNotFoundError(f"The directory {dir} does not exist.")
    # go inside the last created folder
    experiment_list = os.listdir(dir)
    # remove OLD from the list
    experiment_list = [exp for exp in experiment_list if "OLD" not in exp]
    if len(experiment_list) == 0:
        raise FileNotFoundError(f"No experiments found in {dir}.")
    experiment_list.sort()
    last_experiment = experiment_list[-1]
    dir = os.path.join(dir, last_experiment)
    return dir


def compute_number_of_params(list_hidden):
    total_params = 0
    old_layer_size = 0
    for i, layer_size in enumerate(list_hidden):
        if i == 0:
            total_params += 3 * layer_size + layer_size
            old_layer_size = layer_size
        else:
            total_params += layer_size * old_layer_size + layer_size
            old_layer_size = layer_size

    return total_params + layer_size + 1


print(compute_number_of_params([40, 256, 256, 256, 128, 1]))


def masked_list(list, mask):
    return [list[i] for i in range(len(list)) if mask[i]]


if __name__ == "__main__":
    results_dir = ensure_dir(RESULTS_DIR)
    experiment_list = os.listdir(results_dir)
    # go inside the last created folder
    # remove OLD from the list
    experiment_list = [exp for exp in experiment_list if "OLD" not in exp]
    architectures_found = []
    n_params = []
    layers = []
    energy_list = []
    std_energy_list = []
    energy_hist_list = []
    print(f"Found {experiment_list}")
    for experiment in experiment_list:

        name = experiment.split(".")[0].split("_")[:-1]
        print(name)
        hidden_layers = [int(x.replace("d", "")) for x in name]
        try:
            architectures_found.append(hidden_layers + [1])
            n_params.append(compute_number_of_params(hidden_layers))
            layers.append(len(hidden_layers))
            exp_path = os.path.join(results_dir, experiment)
            with open(exp_path + "/final_values.txt", "r") as f:
                lines = f.readlines()
                energy = float(lines[0].strip())
                std_energy = float(lines[1].strip())
                print(f"Experiment: {experiment}, Energy: {energy}, Std: {std_energy}")
            with open(exp_path + "/energy_history.txt", "r") as f:
                energy_hist = [float(x) for x in f.readlines()]
            energy_list.append(energy)
            std_energy_list.append(std_energy)
            energy_hist_list.append(energy_hist)
        except Exception as e:
            print(f"skipping {experiment}")
            print(e)
            n_params.pop()
            architectures_found.pop()
            layers.pop()

    print("found:")
    for arch, n_param, layer_count in zip(architectures_found, n_params, layers):
        print(f"Architecture: {arch}, n_params: {n_param}, layers: {layer_count}")

    plt.figure()
    print(len(n_params), len(energy_list), len(layers))

    different_layers = set(layers)
    for layer_count in different_layers:
        plt.errorbar(
            masked_list(n_params, [x == layer_count for x in layers]),
            masked_list(energy_list, [x == layer_count for x in layers]),
            yerr=masked_list(std_energy_list, [x == layer_count for x in layers]),
            label=f"{layer_count} Hidden Layers",
            fmt="o",
        )

    plt.legend()
    plt.xlabel("Number of Parameters")
    plt.ylabel("Final Energy")
    plt.title("Final Energy vs Number of Parameters")
    plt.hlines(
        DoF / 2,
        xmin=0,
        xmax=max(n_params),
        colors="r",
        linestyles="dashed",
        label="Target Energy",
    )
    plt.savefig("energy_vs_params.png")

    # energy convergence plot
    fig, ax = plt.subplots(
        len(different_layers), 1, figsize=(8, 6 * len(different_layers)), sharex=True
    )
    for i, energy_hist in enumerate(energy_hist_list):
        layer_count = layers[i]
        if len(different_layers) > 1:
            ax[layer_count - 2].plot(energy_hist, label=f"{architectures_found[i]}")
        else:
            plt.plot(energy_hist, label=f"{architectures_found[i]}")
    for ax_i in ax:
        ax_i.hlines(
            DoF / 2,
            xmin=0,
            xmax=max(len(hist) for hist in energy_hist_list),
            colors="r",
            linestyles="dashed",
        )
        ax_i.legend()
        ax_i.set_ylabel("Energy")
    fig.supxlabel("Common X-axis Label")
    plt.tight_layout()
    plt.show()
