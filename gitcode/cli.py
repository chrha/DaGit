
import argparse
import build
import os
import sys
import structure
import pathlib
import textwrap
import subprocess

def parse():
    parser= argparse.ArgumentParser()
    # Add subcommands for git, i.e init, commit etc
    sub_parser= parser.add_subparsers(dest="git command")
    sub_parser.required=True
    #add init command parser
    init_parser= sub_parser.add_parser("init")
    init_parser.set_defaults(func=init)

    #add object hash as command, with a file as argument
    hashobj_parser= sub_parser.add_parser("hash-object")
    hashobj_parser.set_defaults(func=hash_object)
    hashobj_parser.add_argument("file")

    #add cat of an object hash as command, with hash object as argument
    cat_parser= sub_parser.add_parser("cat-file")
    cat_parser.set_defaults(func=cat_file)
    cat_parser.add_argument("object",type=structure.get_goid)

    #add command for creating hash objects for trees
    wtree_parser= sub_parser.add_parser("write-tree")
    wtree_parser.set_defaults(func=write_tree)
    #add command for retrieving tree into directory from hash object
    rtree_parser= sub_parser.add_parser("read-tree")
    rtree_parser.set_defaults(func=read_tree)
    rtree_parser.add_argument("tree",type=structure.get_goid)

    commit_parser= sub_parser.add_parser("commit")
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument('-m', '--message', required=True)

    log_parser= sub_parser.add_parser("log")
    log_parser.set_defaults(func=log)
    log_parser.add_argument ('goid',default='@',type=structure.get_goid, nargs='?')

    checkout_parser= sub_parser.add_parser("checkout")
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument("commit")

    tag_parser = sub_parser.add_parser ('tag')
    tag_parser.set_defaults (func=tag)
    tag_parser.add_argument ('name')
    tag_parser.add_argument ('goid',default='@',type=structure.get_goid ,nargs='?')

    k_parser = sub_parser.add_parser ('k')
    k_parser.set_defaults (func=k)


    branch_parser = sub_parser.add_parser ('branch')
    branch_parser.set_defaults (func=branch)
    branch_parser.add_argument ('name')
    branch_parser.add_argument ('start_point',default='@',type=structure.get_goid ,nargs='?')

    return parser.parse_args()


def init(args):
    build.init()
    print('initialized an empty dagit directory at' + os.path.join(os.getcwd(),build.GIT_DIR) )

def hash_object(args):
    with open (args.file,"rb") as f:
        print(build.hash_obj(f.read()))

def cat_file(args):
    sys.stdout.flush()
    sys.stdout.buffer.write(build.get_obj(args.object, expected=None))

def write_tree(args):
    print(structure.write_tree())

def read_tree(args):
    structure.read_tree(args.tree)

def commit(args):
    print(structure.commit(args.message))

def log (args):

    #goid = args.goid or build.get_ref('HEAD')
    #goid=args.goid
    #while goid:
    for goid in structure.get_commit_and_parents({args.goid}):
        commit = structure.get_commit (goid)

        print ("commit "+ goid + '\n')
        print (textwrap.indent (commit.message, '    '))
        print ('')

        goid = commit.parent

def checkout(args):
    structure.checkout(args.commit)

def tag(args):
    #goid = args.goid or build.get_ref('HEAD')
    structure.create_tag(args.name, args.goid)

def k(args):
    dot = 'digraph commits {\n'
    goids=set()
    for ref, name in build.iter_refs(deref=False):
        dot += f'"{ref}" [shape=note]\n'
        dot += f'"{ref}" -> "{name.value}"\n'
        if not name.symbolic:
            goids.add(name.value)
    for goid in structure.get_commit_and_parents(goids):
        commit= structure.get_commit(goid)
        dot += f'"{goid}" [shape=box style=filled label="{goid[:10]}"]\n'
        if commit.parent:
            dot += f'"{goid}" -> "{commit.parent}"\n'

    dot += '}'
    print (dot)

    with subprocess.Popen (
            ['dot', '-Tx11', '/dev/stdin'],
            stdin=subprocess.PIPE) as proc:
        proc.communicate (dot.encode ())

def branch(args):
    structure.create_branch(args.name, args.start_point)
    print("Branch " + args.name +"  created at " + args.start_point[:10])


def main():
    args=parse()
    args.func(args)

main()
