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
        # Spatial coordinates of the geographic position for the implantation
        # of the geometrical data (cave or tunnel-system)
        geo_offset=[1841790.636546, 5175201.482763, 200.0],
        # The workflow generates a 3DTiles tileset with multiple Level Of Details
        # (LODs). Define how many LODS are required
        threedtiles_number_of_lods=4,
        # Every LOD has a geometric resolution threshold (at which observation
        # distance will each respective LOD be visible). The following map has
        # the number of lods as key and the associated geometric errors
        # (as many values as lods) as values
        threedtiles_thresholds={4: [0.10, 0.45, 0.75, 1.05]},
    ),
)
