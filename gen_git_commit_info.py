import hashlib
import os
import shutil
import subprocess
import zlib

repo_dir = 'repo.tmp'
git_dir = b'.git'
objects_dir = os.path.join(git_dir, b'objects')

# Tree parameters.
default_blob_basename = b'a'
default_blob_content = b'a'
default_blob_mode = b'100644'

# Commit parameters.
default_name = b'a'
default_email = b'a@a.com'
# 2000-01-01T00:00:00+0000
default_date_s = 946684800
default_tz = b'+0000'
default_author_date_s = default_date_s
default_author_date_tz = default_tz
default_author_email = default_email
default_author_name = default_name
default_committer_date_s = default_date_s
default_committer_date_tz = default_tz
default_committer_email = default_email
default_committer_name = default_name
default_message = b'a'
# ASCII hex of parents.
default_parents = ()


def init():
    for d in (repo_dir, 'clone.tmp'):
        shutil.rmtree(d, ignore_errors=True)
    os.mkdir(repo_dir)
    os.chdir(repo_dir)
    subprocess.check_output(['git', 'init', '-q'])


def get_object_and_sha(obj_type, content):
    obj = b'%s %s\0%s' % (obj_type, str(len(content)).encode('ascii'), content)
    hash = hashlib.sha1(obj)
    return (obj, hash.hexdigest().encode('ascii'), hash.digest())


def save_object(obj_type, content):
    obj, sha_ascii, sha = get_object_and_sha(obj_type, content)
    obj_dir = os.path.join(objects_dir, sha_ascii[:2])
    obj_path = os.path.join(obj_dir, sha_ascii[2:])
    os.makedirs(obj_dir, exist_ok=True)
    with open(obj_path, 'wb') as f:
        f.write(zlib.compress(obj))
    return sha_ascii, sha


# TODO multiple children object.
def save_tree_object(mode, basename, sha):
    tree_content = b'%s %s\0%s' % (mode, basename, sha)
    return save_object(b'tree', tree_content) + (tree_content,)


def save_commit_object(
        tree_sha_ascii,
        parents=default_parents,
        author_name=default_author_name,
        author_email=default_author_email,
        author_date_s=default_author_date_s,
        author_date_tz=default_author_date_tz,
        committer_name=default_committer_name,
        committer_email=default_committer_email,
        committer_date_s=default_committer_date_s,
        committer_date_tz=default_committer_date_tz,
        message=default_message):
    if parents and parents[0]:
        parents_bytes = b''
        sep = b'\nparent '
        parents_bytes = sep + sep.join(parents) + b'\n'
    else:
        parents_bytes = b'\n'
    commit_content = b'tree %s%sauthor %s <%s> %s %s\ncommitter %s <%s> %s %s\n\n%s\n' % (
        tree_sha_ascii, parents_bytes,
        author_name, author_email, str(author_date_s).encode('ascii'), author_date_tz,
        committer_name, committer_email, str(committer_date_s).encode('ascii'), committer_date_tz,
        message)
    return save_object(b'commit', commit_content) + (commit_content,)


def get_git_hash_object(obj_type, input):
    cmd = [b'git', b'hash-object', b'--stdin', b'-t', obj_type]
    return subprocess.check_output(cmd, input=input).rstrip()


def create_tree_with_one_file(
        blob_mode=default_blob_mode,
        blob_basename=default_blob_basename,
        blob_content=default_blob_content,
):
    blob_sha_ascii, blob_sha = save_object(b'blob', blob_content)
    tree_sha_ascii, tree_sha, tree_content = save_tree_object(blob_mode, blob_basename, blob_sha)
    return tree_sha_ascii


if __name__ == '__main__':
    init()
    x = create_tree_with_one_file()
    save_commit_object(tree_sha_ascii=x)
