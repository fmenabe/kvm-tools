# -*- coding: utf-8 -*-

import os
import unix
import kvm
import pprint
import lib.utils as utils


def get_interfaces():
    logger.debug('Getting interfaces', args.name)
    interfaces = []
    if args.interfaces is None:
        logger.error('No interfaces!', args.name, True)
    else:
        is_first = True
        for interface in args.interfaces:
            # 'interface' is a string with elements separeted by commas if
            # comming from the command-line but a list if comming from a YAML
            # file! Make sure we treat a list.
            if type(interface) is str:
                interface = interface.split(',')

            if (
              (is_first and len(interface) != 4)
              or (not is_first and len(interface) != 3)
            ):
                logger.error(
                    "Invalid interface '%s'" % interface, args.name, True)
            is_first = False

            cur_interface = {
                'mac': kvm.gen_mac(),
                'driver': 'virtio',
                'address': interface[0],
                'netmask': interface[1]
            }
            if len(interface) == 3:
                cur_interface.setdefault('vlan', interface[2])
            else:
                cur_interface.setdefault('gateway', interface[2])
                cur_interface.setdefault('vlan', interface[3])
            interfaces.append(cur_interface)

        logger.debug(pprint.pformat(interfaces))
        return interfaces


def get_disks():
    logger.debug('Getting disks', args.name)
    disks = [{
        'path': os.path.join(
            args.dst_disks,
            '%s.%s' % (args.name, args.format)
        ),
        'format': args.format,
        'driver': 'virtio',
        'device': 'vda'
    }]
    if args.disks:
        for (index, disk) in enumerate(args.disks):
            if type(disk) is str:
                try:
                    suffix, size = disk.split(',')
                    size = int(size)
                except (IndexError, ValueError):
                    logger.error("Invalid disk '%s'" % disk, args.name, True)
            else:
                suffix, size = disk

            disks.append({
                'path': os.path.join(args.dst_disks, '%s-%s.%s' % (
                    args.name, suffix, args.format)),
                'format': args.format,
                'driver': 'virtio',
                'device': 'vd%s' % chr(index + 98),
                'size': size
            })

    logger.debug(pprint.pformat(disks))
    return disks


def check_args():
    logger.info("Checking parameters", args.name)
    logger.debug(pprint.pformat(vars(args)))
    if args.dst_host is None:
        logger.error('No destination host!', args.name, True)

    if args.model not in utils.MODELS:
        logger.error('Invalid model!', args.name, True)

    # Get interfaces in an exploitable form.
    interfaces = get_interfaces()

    # Get disks in an exploitable form.
    disks = get_disks()

    return (interfaces, disks)


def connect():
    logger.info(
        "Connecting to source hypervisor '%s'" % args.src_host, args.name)

    try:
        src_host = kvm.KVM(unix.linux.Deb(unix.Remote()))
        src_host.connect(args.src_host)
    except unix.ConnectError as cerr:
        logger.error('Unable to connect: %s' % cerr, args.name, True)

    logger.info(
        "Connecting to destination hypervisor '%s'" % args.dst_host, args.name)

    try:
        dst_host = kvm.KVM(unix.linux.Deb(unix.Remote()))
        dst_host.connect(args.dst_host)
    except unix.ConnectError as cerr:
        logger.error('Unable to connect: %s' % cerr, args.name, True)

    return (src_host, dst_host)


def deploy():
    logger.info('Beginning deployment', args.name)

    # Check arguments.
    interfaces, disks = check_args()

    # Connect to source and destination hosts.
    src_host, dst_host = connect()


def main(args):
    # 'main' function is only the entry point of the command. Make 'args'
    # global to the file.
    globals()['args'] = args
    global logger
    logger = utils.Logger('deploy', args.loglevel, args.logfile)

    # Per guest deployment.
    if args.name is not None:
        try:
            deploy()
        except utils.QuitOnError:
            sys.exit(1)
    # Multi guests deployment.
    # TODO: use multiprocessing for parallelizing deployment.
    else:
        import yaml
        guests = yaml.load(open(args.file))
        for guest, guest_conf in guests.iteritems():
            # Get parameters from the file, otherwise from command-line.
            guest_params = dict(
                ((arg, guest_conf[arg] if arg in conf else value)
                    for arg, value in args.iteritems())
            )
            guest_params['name'] = guest
            try:
                deploy(guest_params)
            except utils.QuitOnError:
                pass
