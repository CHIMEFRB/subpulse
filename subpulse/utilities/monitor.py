from chime_frb_api import frb_master
master = frb_master.FRBMaster()
master.swarm.monitor_jobs("subpulse-toa")
