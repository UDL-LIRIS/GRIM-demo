import types
from hera_k8s_utils.num_exp_environment import num_exp_environment, Struct


class environment(num_exp_environment):

    def __init__(self, args, verbose=False):
        num_exp_environment.__init__(self, args, verbose)
        # Just to make sure the cluster is accessible. Note that this check is
        # not necessary since it is already done in the above constructor
        self.k8s.assert_cluster()

        ### A persistent volume (defined at the k8s level) can be used by
        # tasks of a workflow in order to flow output results from an upstream
        # task to a downstream one, and persist once the workflow is finished
        self.k8s.assert_volume_claim(args.k8s_volume_claim_name)

        # The information that are "close/related" to runtime cluster.
        self.cluster = types.SimpleNamespace(
            docker_registry="harbor.pagoda.os.univ-lyon1.fr",
            docker_organisation="vcity",
            configmap=args.k8s_configmap_name,
        )

        ### We now store the information required by the tasks in order to
        # consume/use that volume
        self.persisted_volume = Struct()
        self.persisted_volume.claim_name = args.k8s_volume_claim_name

        # The mount point/path is technicality standing in between Environment and
        # Experiment related notions: more precisely it is a technicality that
        # should be dealt by the (Experiment) Conductor (refer to
        # https://gitlab.liris.cnrs.fr/expedata/expe-data-project/-/blob/master/lexicon.md#conductor )
        self.persisted_volume.mount_path = "/within-container-mount-point"
