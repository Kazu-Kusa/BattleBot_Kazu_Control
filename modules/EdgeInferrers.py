from modules.AbsEdgeInferrer import AbstractEdgeInferrer
from repo.uptechStar.module.actions import ActionPlayer, new_action_frame


class StandardEdgeInferrer(AbstractEdgeInferrer):
    def do_fl(self) -> bool:
        """
        [fl]         fr
            O-----O
               |
            O-----O
        rl           rr

        front-left encounters the edge, turn right,turn type is 1
        """
        pass

    def do_nothing(self) -> bool:
        return False

    def stop(self) -> bool:
        self.player.append(new_action_frame())
        self.player.play()
        return True

    player = ActionPlayer()

    def floating_inferrer(self, edge_sensors: tuple[int, int, int, int],
                          *args, **kwargs) -> tuple[bool, bool, bool, bool]:
        # TODO: there is a chance to pre-bake the search table,but may takes more time
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
