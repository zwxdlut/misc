import os
# import sys

# from loguru import logger


def parser_config():
    import yaml

    cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(cwd, "config/mxdataset.yaml")) as file:
        cfg = yaml.safe_load(file)

    return cfg


def config_log(name, output_dir):
    global logger
    logger = logger.bind(name=name)
    # logger.add(sys.stdout, level='DEBUG')

    os.makedirs(output_dir, exist_ok=True)
    log_file_path = os.path.join(output_dir, f"log_{name}.log")
    # if os.path.exists(log_file_path):
    #     os.remove(log_file_path)
    log_handle = logger.add(log_file_path)

    logger.info(
        "======================config log finished=====================")
    logger.info("[config_log] log file path:{}".format(log_file_path))

    return log_handle


# EOF
