import logging
import argparse
import importlib
import functools

import krpc

from stages.BaseStage import BaseStage

log = logging.getLogger('main')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', default=krpc.DEFAULT_ADDRESS)
    parser.add_argument('--rpc-port', type=int, default=krpc.DEFAULT_RPC_PORT)
    parser.add_argument('--stream-port', type=int, default=krpc.DEFAULT_STREAM_PORT)
    parser.add_argument('--client-name', default='Program')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('program')
    args = parser.parse_args()

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level)

    conn = krpc.connect(name=args.client_name,
                        address=args.address,
                        rpc_port=args.rpc_port,
                        stream_port=args.stream_port)
    log.info('Connected to %s', args.address)
    vessel = conn.space_center.active_vessel

    program = eval('[{}]'.format(args.program), {}, ProgramLocals(conn, vessel))
    program = [init_stage(stage) for stage in program]

    log.info('Program: %s', program)

    for stage in program:
        stage()

    log.info('Program complete')


class ProgramLocals:
    def __init__(self, conn, vessel):
        self.conn = conn
        self.vessel = vessel

    def __getitem__(self, key):
        stage_name = key
        stage_module = importlib.import_module('stages.' + stage_name)
        stage_class = getattr(stage_module, stage_name)
        return functools.partial(stage_class, self.conn, self.vessel)


def init_stage(stage):
    if not isinstance(stage, BaseStage):
        stage = stage()
    return stage


if __name__ == '__main__':
    main()
