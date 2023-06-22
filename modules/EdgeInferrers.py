from modules.AbsEdgeInferrer import AbstractEdgeInferrer


class StandardEdgeInferrer(AbstractEdgeInferrer):

    def floating_inferrer(self, edge_sensors: tuple[int, int, int, int],
                          *args, **kwargs) -> tuple[bool, bool, bool, bool]:
        edge_rr_sensor = edge_sensors[0]
        edge_fr_sensor = edge_sensors[1]
        edge_fl_sensor = edge_sensors[2]
        edge_rl_sensor = edge_sensors[3]
        edge_baseline = kwargs.get('edge_baseline')
        min_baseline = kwargs.get('min_baseline')
        return (edge_fl_sensor > edge_baseline and edge_fl_sensor > min_baseline,
                edge_fr_sensor > edge_baseline and edge_fr_sensor > min_baseline,
                edge_rl_sensor > edge_baseline and edge_rl_sensor > min_baseline,
                edge_rr_sensor > edge_baseline and edge_rr_sensor > min_baseline)
