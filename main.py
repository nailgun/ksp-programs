import logging
import argparse
import importlib
import functools

import krpc

from watcher import Watcher
from stages.BaseStage import BaseStage

log = logging.getLogger('main')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', default=krpc.DEFAULT_ADDRESS)
    parser.add_argument('--rpc-port', type=int, default=krpc.DEFAULT_RPC_PORT)
    parser.add_argument('--stream-port', type=int, default=krpc.DEFAULT_STREAM_PORT)
    parser.add_argument('--client-name', default='Program')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--quicksave', action='store_true')
    parser.add_argument('--quickload', action='store_true')
    parser.add_argument('--no-autodecouple', action='store_true')
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

    if args.quickload:
        log.info('Loading quicksave as requested')
        conn.space_center.quickload()

    vessel = conn.space_center.active_vessel

    watcher_thread = Watcher(conn, vessel)
    watcher_thread.start()

    program = eval('[{}]'.format(args.program), {}, ProgramLocals(conn, vessel, watcher_thread))
    program = [init_stage(stage) for stage in program]
    log.info('Program: %s', program)

    for stage in program:
        log.info('Executing stage %s', stage)
        watcher_thread.autodecouple = stage.autodecouple and not args.no_autodecouple
        stage()
        if args.quicksave:
            log.info('Quicksaving as requested')
            conn.space_center.quicksave()

    log.info('Program complete')


class ProgramLocals:
    def __init__(self, conn, vessel, watcher):
        self.conn = conn
        self.vessel = vessel
        self.watcher = watcher

    def __getitem__(self, key):
        stage_name = key
        stage_module = importlib.import_module('stages.' + stage_name)
        stage_class = getattr(stage_module, stage_name)
        return functools.partial(stage_class, self.conn, self.vessel, self.watcher)


def init_stage(stage):
    if not isinstance(stage, BaseStage):
        stage = stage()
    return stage


if __name__ == '__main__':
    main()
