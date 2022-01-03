import logging
import warnings


def configure_logger(level=logging.INFO):
    log_format = f'[%(asctime)-15s] [%(levelname)s] [%(name)s]  %(message)s'

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    #
    # logging.getLogger('pyrogram.session.session').setLevel(logging.WARNING)
    # logging.getLogger('pyrogram.connection.connection').setLevel(logging.WARNING)
    # logging.getLogger('aiohttp.access').setLevel(logging.WARNING)
    # logging.getLogger('pyrogram.client.client').setLevel(logging.WARNING)
    # logging.getLogger('pyrogram.client.ext.syncer').setLevel(logging.WARNING)
    # logging.getLogger('pyrogram.connection.transport.tcp.tcp').setLevel(logging.WARNING)
    # logging.getLogger('apscheduler.executors.default').setLevel(logging.ERROR)

    warnings.filterwarnings("ignore")
