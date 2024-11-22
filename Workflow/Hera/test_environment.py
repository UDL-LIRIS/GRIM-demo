# Assert the ArgoWorkflow engine (designated by the "hera.config" configuration
# file) is reachable
if __name__ == "__main__":

    from parser import parser
    from environment import environment

    args = parser().parse_args()
    environment = environment(args)
