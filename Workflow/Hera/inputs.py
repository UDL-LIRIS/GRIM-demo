import types

inputs = types.SimpleNamespace(
    constants=types.SimpleNamespace(
        # Constants (a.k.a. fixed parameters): such parameter values are not
        # sweeped (in other terms they are unique values). and are thus shared by all the computations.
        experiment_output_dir="junk",
    ),
    parameters=types.SimpleNamespace(
        # Parameters vary independently from one another
        subdivision_level=1,
        mesh2vol_resolution=100,  # 100 for cave and 300 for tunnels
    ),
)
