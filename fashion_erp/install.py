from fashion_erp.patches.v1_0.seed_phase1_master_data import execute


def after_install() -> None:
    execute()
