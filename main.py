import logging
import argparse
import importlib

import krpc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', default=krpc.DEFAULT_ADDRESS)
    parser.add_argument('--rpc-port', type=int, default=krpc.DEFAULT_RPC_PORT)
    parser.add_argument('--stream-port', type=int, default=krpc.DEFAULT_STREAM_PORT)
    parser.add_argument('--client-name', default='Program')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level)
    log = logging.getLogger('main')

    program = ['Launch', 'Ascend', 'Circularize']
    # program = ['Circularize']
    log.info('Program: %s', ', '.join(program))

    conn = krpc.connect(name=args.client_name,
                        address=args.address,
                        rpc_port=args.rpc_port,
                        stream_port=args.stream_port)
    log.info('Connected to %s', args.address)

    vessel = conn.space_center.active_vessel

    for stage_name in program:
        log.info('Executing stage %s', stage_name)
        stage_module = importlib.import_module('stages.' + stage_name)
        stage_class = getattr(stage_module, stage_name)
        stage = stage_class(conn, vessel)
        stage()

    log.info('Program complete')


if __name__ == '__main__':
    main()
