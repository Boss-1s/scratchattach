import scratchattach as sa
from scratchattach.cloud.cloud import CustomCloud

# Init Server & Cloud Events

server_ip = '0.0.0.0'
server_port = 8080
project_id="1321224718"

server = sa.init_cloud_server("0.0.0.0",
                              server_port,
                              length_limit=65536,
                              allow_non_numeric=True,
                              whitelisted_projects=[project_id],
                              allow_nonscratch_names=True,
                              blocked_ips=[],
                              sync_players=True,
                              log_var_sets=True
                              )
server.start()

cloud = CustomCloud(project_id=project_id,
                    cloud_host=f"ws://{server_ip}:{server_port}",
                    username = "Boss_1s",
                    length_limit = None,
                    allow_non_numeric = True,
                    _session = None,
                    header = None,
                    cookie = None,
                    origin = None,
                    print_connect_messages = True
                    )
cloud_events=cloud.events()