"""@summary Run real isolated SDK provenance negative fixtures without altering canonical sources."""
import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
from test_sdk_provenance import load_lock, require, verify

ROOT = Path(__file__).resolve().parents[1]


def run(command):
    """@summary Execute a bounded local command without a shell. @param command Argument vector. @return Captured result."""
    return subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)


def git(root, *arguments):
    """@summary Read or operate on an explicitly prepared local Git fixture. @param root Repository. @param arguments Git arguments. @return Captured stdout."""
    result = run(['git', '-C', str(root), *arguments])
    require(result.returncode == 0, result.stderr)
    return result.stdout.strip()


def plain_directory(path, allow_absent=False):
    """@summary Reject reparse metadata ancestors before Git operations. @param path Absolute native directory. @param allow_absent Permit absent final component. @return Whether directory exists."""
    require(path.is_absolute(), 'Absolute metadata path required')
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            value = current.lstat()
        except FileNotFoundError:
            require(allow_absent and current == path, 'Missing metadata ancestor')
            return False
        require(stat.S_ISDIR(value.st_mode) and not getattr(value, 'st_file_attributes', 0) & 0x400,
                'Nonordinary Git metadata directory')
    return True


def metadata(root, revision):
    """@summary Reject executable inherited Git policy before clone, checkout or status. @param root Plain local repository. @param revision Committed tree used for precheckout attributes."""
    plain_directory(root)
    plain_directory(root / '.git')
    git_dir = Path(git(root, 'rev-parse', '--absolute-git-dir'))
    require(os.path.normcase(os.path.abspath(git_dir)) == os.path.normcase(os.path.abspath(root / '.git')),
            'Unexpected Git directory')
    hooks = git_dir / 'hooks'
    if plain_directory(hooks, True):
        for entry in hooks.iterdir():
            value = entry.lstat()
            require(stat.S_ISREG(value.st_mode) and not getattr(value, 'st_file_attributes', 0) & 0x400
                    and entry.name.endswith('.sample'), 'Active or reparse Git hook requires review')
    for key in ('core.hooksPath', 'core.fsmonitor', 'core.attributesFile'):
        result = run(['git', '-C', str(root), 'config', '--get', key])
        require(result.returncode == 1 and not result.stdout, 'Custom Git policy requires review: ' + key)
    files = git(root, 'ls-tree', '-r', '--name-only', revision).splitlines()
    require(bool(files), 'Empty SDK tree')
    attributes = git(root, 'check-attr', '--source=' + revision, '-z',
                     'filter', 'working-tree-encoding', '--', *files).split('\0')
    require(len(attributes) == len(files) * 6 + 1, 'Incomplete attribute preflight')
    for offset in range(0, len(attributes) - 1, 3):
        require(attributes[offset] in files and attributes[offset + 1] in ('filter', 'working-tree-encoding')
                and attributes[offset + 2] in ('unspecified', 'unset'), 'Custom Git filter or encoding requires review')
    # @summary Inspect effective worktree overrides too; no clean/smudge operation is invoked.
    attributes = git(root, 'check-attr', '-z', 'filter', 'working-tree-encoding', '--', *files).split('\0')
    require(len(attributes) == len(files) * 6 + 1, 'Incomplete effective attribute preflight')
    for offset in range(0, len(attributes) - 1, 3):
        require(attributes[offset + 2] in ('unspecified', 'unset'), 'Custom effective Git filter or encoding requires review')


def clone_fixture(source, destination, template, revision):
    """@summary Prepare a real isolated SDK copy with metadata checks before checkout. @param source Prepared clean SDK. @param destination New exclusive directory. @param template Empty explicit template. @param revision Pinned committed revision. @return Fixture root."""
    metadata(source, revision)
    require(git(source, 'rev-parse', 'HEAD') == revision and not git(source, 'status', '--porcelain', '--untracked-files=normal'),
            'Fixture input requires exact clean SDK')
    result = run(['git', 'clone', '--no-hardlinks', '--no-checkout', '--template=' + str(template),
                  str(source), str(destination)])
    require(result.returncode == 0, result.stderr)
    metadata(destination, revision)
    git(destination, '-c', 'core.autocrlf=false', 'checkout', '--detach', revision)
    metadata(destination, revision)
    require(not git(destination, 'status', '--porcelain', '--untracked-files=normal'), 'Cloned SDK is dirty')
    return destination


def fixture(work, name, lock):
    """@summary Prepare only lock and vendored TypeScript inputs. @param work Exclusive output. @param name Case name. @param lock Lock content. @return Fixture root."""
    root = work / name
    artifact = root / lock['vendored_path']
    artifact.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / lock['vendored_path'], artifact)
    (root / 'sdk.lock.json').write_text(json.dumps(lock, indent=2) + '\n', encoding='utf-8')
    return root


def expect(work, name, root, sdk, diagnostic=''):
    """@summary Verify real inputs and require the intended failure category. @param work Exclusive evidence owner. @param name Case name. @param root Fixture root. @param sdk Real explicit SDK. @param diagnostic Empty for success or required exception diagnostic."""
    observed = ''
    try:
        verify(str(sdk), root)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        observed = str(error)
    (work / (name + '.log')).write_text(observed or 'Verified actual provenance\n', encoding='utf-8')
    require(bool(observed) and diagnostic in observed if diagnostic else not observed,
            name + ': unexpected provenance outcome; see retained log')


def integrity(work, sdk):
    """@summary Exercise clean, revision, dirty, missing, tampered and closed-schema cases. @param work Fresh exclusive directory. @param sdk Prepared exact clean SDK."""
    lock = load_lock(ROOT)
    revision = lock['revision']
    metadata(sdk, revision)
    require(git(sdk, 'rev-parse', 'HEAD') == revision and not git(sdk, 'status', '--porcelain', '--untracked-files=normal'),
            'Explicit SDK must be clean and pinned')
    expect(work, 'valid', fixture(work, 'valid', lock), sdk)
    offline = fixture(work, 'valid-offline', lock)
    verify('', offline)
    expect(work, 'missing-sdk', fixture(work, 'missing-sdk', lock), work / 'absent-sdk', 'Missing explicit SDK source')
    wrong = copy.deepcopy(lock)
    wrong['revision'] = '0' * 40
    expect(work, 'wrong-revision', fixture(work, 'wrong-revision', wrong), sdk, 'SDK requires exact clean pinned revision')
    for mode in ('missing', 'tampered'):
        source = fixture(work, mode + '-vendored', lock)
        path = source / lock['vendored_path']
        if mode == 'missing':
            path.unlink()
        else:
            path.write_bytes(path.read_bytes() + b'\nchanged fixture\n')
        expect(work, mode + '-vendored', source, sdk,
               'Missing SDK payload' if mode == 'missing' else 'Modified SDK compatibility artifact')
    # @summary Hash mismatches use the genuinely clean SDK, so the later profile predicates are reached.
    for field, diagnostic in (('manifest_sha256', 'SDK manifest hash mismatch'),
                              ('declaration_sha256', 'SDK profile declaration hash mismatch'),
                              ('guide_sha256', 'SDK profile guide hash mismatch')):
        wrong = copy.deepcopy(lock)
        (wrong if field == 'manifest_sha256' else wrong['profile'])[field] = '0' * 64
        expect(work, field, fixture(work, field, wrong), sdk, diagnostic)
    for section in ('lock', 'profile'):
        original = lock if section == 'lock' else lock['profile']
        for key in original:
            for mutation in ('missing', 'wrong-type'):
                wrong = copy.deepcopy(lock)
                target = wrong if section == 'lock' else wrong['profile']
                if mutation == 'missing':
                    del target[key]
                else:
                    target[key] = True if key == 'schema_version' else 7
                name = section + '-' + key + '-' + mutation
                # @summary Schema fixtures must still contain the preserved payload at its fixed path.
                source = fixture(work, name, lock)
                (source / 'sdk.lock.json').write_text(json.dumps(wrong), encoding='utf-8')
                expect(work, name, source, sdk, 'Invalid SDK')
        wrong = copy.deepcopy(lock)
        (wrong if section == 'lock' else wrong['profile'])['unexpected'] = 'field'
        name = section + '-extra-key'
        source = fixture(work, name, lock)
        (source / 'sdk.lock.json').write_text(json.dumps(wrong), encoding='utf-8')
        expect(work, name, source, sdk, 'Invalid SDK')
    template = work / 'empty-template'
    template.mkdir()
    for mode in ('tracked', 'untracked', 'canonical-tamper', 'canonical-missing'):
        clone = clone_fixture(sdk, work / ('sdk-' + mode), template, revision)
        relative = {'tracked': 'README.md', 'untracked': 'fixture-untracked.txt',
                    'canonical-tamper': 'TypeScript/simoder.d.ts', 'canonical-missing': 'TypeScript/simoder.d.ts'}[mode]
        path = clone / relative
        if mode == 'canonical-missing':
            path.unlink()
        else:
            path.write_bytes(b'dirty fixture\n')
        metadata(clone, revision)
        expect(work, mode, fixture(work, mode, lock), clone, 'SDK requires exact clean pinned revision')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sdk-source', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, required=True)
    args = parser.parse_args()
    work = args.work_dir.absolute()
    work.mkdir(parents=True, exist_ok=False)
    integrity(work, args.sdk_source.absolute())
    print('PASS: actual SDK provenance integrity cases')


