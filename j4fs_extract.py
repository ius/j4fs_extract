#!/usr/bin/python2
import argparse, struct, sys, os

S_INODE = '8I128s'

J4FS_MAGIC = 0x87654321
J4FS_FILE_MAGIC = 0x12345678

def write_file(filename, length, fp):
    """ Write file data to file """
    if not os.path.isdir(args.dir):
        os.mkdir(args.dir)

    path = os.path.join(args.dir, filename)
    print path

    ofp = open(path, 'w')

    while length > 0:
        nbyte = min(8192, length)
        ofp.write(fp.read(nbyte))
        length -= nbyte

    ofp.close()

def j4fs_inode_is_valid(inode):
    """ Determine whether specified inode is valid (ie. not deleted) """
    flags = inode[4]

    return (flags & 0x01) == ((flags & 0x02) >> 1)

def j4fs_inode_is_last(inode):
    """ Determine whether specified inode is the last one """
    link = inode[0]
    flags = inode[4]

    return (link == 0xffffffff and (flags & 0x01) == 0x01) or \
           (link == 0x00000000 and (flags & 0x01) == 0x00)

def j4fs_extract(fp):
    # first ro entry is past mst
    link = args.block_size
    inode = None

    while not inode or not j4fs_inode_is_last(inode):
        inode_pos = link
        fp.seek(link)

        inode_data = fp.read(struct.calcsize(S_INODE))
        inode = list(struct.unpack(S_INODE, inode_data))

        # inode (link, size, type, offset, flags, stroff, id, length, filename)
        link, _, type, _, flags, _, _, length, filename = inode

        assert type == J4FS_FILE_MAGIC, 'Unknown inode type'

        filename = filename.split('\x00')[0]

        # data is at inode_pos + page_size
        fp.seek(inode_pos + args.page_size)

        write_file(filename, length, fp)

def j4fs_image_valid(fp):
    """ Check whether fp is a valid j4fs image """
    fp.seek(0)

    magic, = struct.unpack('I', fp.read(4))

    return (magic == J4FS_MAGIC)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract j4fs/lfs images')
    parser.add_argument('file', help='input image')
    parser.add_argument('-o', dest='dir', help='output directory', default='out')
    parser.add_argument('-p', dest='page_size', type=int, help='page size (default 4096)', default=4096)
    parser.add_argument('-b', dest='block_size', type=int, help='block size (default 262144)', default=262144)

    args = parser.parse_args()

    fp = None

    try:
        fp = open(args.file)

        if not j4fs_image_valid(fp):
            print >> sys.stderr, 'Error: input file does not appear to contain a valid j4fs filesystem'
            sys.exit(1)

    except IOError, e:
        print >> sys.stderr, e
        sys.exit(1)

    print 'Writing files to %r\n' % args.dir
    j4fs_extract(fp)

    fp.close()

