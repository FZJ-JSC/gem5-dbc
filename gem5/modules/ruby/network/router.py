import m5

from modules.options import Options

from modules.util import fatal_error


def create(options: Options, router_id, latency = 1, router_class = 0):
    """
    Create network router
    """

    model  = options.architecture.NOC.network.model
    router = None

    if model == "garnet":
        router = m5.objects.GarnetRouter(
                    router_id = router_id,
                    latency   = latency,
                    router_class = router_class
                )
    elif model == "simple":
        router = m5.objects.Switch(
                    router_id = router_id,
                    latency   = latency,
                    router_class = router_class
                )
    else:
        fatal_error(f"Unknown network {model}")


    return router
