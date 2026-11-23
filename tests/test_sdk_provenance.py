"""@summary Verify closed SDK 0.2 profile provenance and the preserved TypeScript copy."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def require(condition, diagnostic):
    """@summary Reject an invalid contract even under optimized Python. @param condition Predicate. @param diagnostic Failure category."""
    if not condition:
        raise ValueError(diagnostic)


def read_json(path):
    """@summary Read JSON while rejecting ambiguous duplicate keys. @param path Input file. @return Parsed value."""
    def unique(pairs):
        """@summary Require distinct object keys. @param pairs Decoder pairs. @return Closed object."""
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate SDK JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def digest(path):
    """@summary Hash a regular non-symlink payload. @param path Payload file. @return SHA-256 hex."""
    require(path.is_file() and not path.is_symlink(), 'Missing SDK payload: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_lock(root):
    """@summary Validate exact schema-2 lock keys and scalar types. @param root Examples source root. @return Validated lock."""
    lock = read_json(root / 'sdk.lock.json')
    keys = {'repository', 'revision', 'canonical_path', 'vendored_path', 'sha256',
            'schema_version', 'package_version', 'manifest_sha256', 'profile'}
    require(type(lock) is dict and set(lock) == keys, 'Invalid SDK lock schema keys')
    require(type(lock['schema_version']) is int and lock['schema_version'] == 2,
            'Invalid SDK lock schema version')
    for key in keys - {'schema_version', 'profile'}:
        require(type(lock[key]) is str, 'Invalid SDK lock field type: ' + key)
    require(lock['repository'] in ('https://github.com/SimCity13-Modders/Simoder-SDK.git', 'git@TailedKarpier:MiamiCenter/Simoder-SDK.git')
            and lock['canonical_path'] == 'TypeScript/simoder.d.ts'
            and lock['vendored_path'] == 'examples/TypeScriptExample/scripts/simoder.d.ts'
            and lock['package_version'] == '0.2.0', 'Invalid SDK lock identity')
    require(re.fullmatch(r'[0-9a-f]{40}', lock['revision']) is not None, 'Invalid SDK revision')
    profile = lock['profile']
    require(type(profile) is dict and set(profile) == {'name', 'declaration_path',
            'declaration_sha256', 'guide_path', 'guide_sha256'}, 'Invalid SDK profile schema keys')
    require(all(type(value) is str for value in profile.values()), 'Invalid SDK profile field type')
    require(profile['name'] == 'base-luau-alpha-v1' and profile['declaration_path'] == 'Luau/base.d.luau'
            and profile['guide_path'] == 'Luau/BASE_API.md', 'Invalid SDK profile identity')
    for value in (lock['sha256'], lock['manifest_sha256'], profile['declaration_sha256'], profile['guide_sha256']):
        require(re.fullmatch(r'[0-9a-f]{64}', value) is not None, 'Invalid SDK SHA-256')
    return lock


def verify(sdk_source, root=None):
    """@summary Check local bytes and optional exact clean canonical profile. @param sdk_source Explicit checkout or empty string. @param root Optional isolated Examples fixture root."""
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    lock = load_lock(root)
    artifact = root / lock['vendored_path']
    require(digest(artifact) == lock['sha256'], 'Modified SDK compatibility artifact')
    if sdk_source:
        sdk = Path(sdk_source)
        require(sdk.is_dir(), 'Missing explicit SDK source')
        revision = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD']).decode().strip()
        status = subprocess.check_output(['git', '-C', str(sdk), 'status', '--porcelain', '--untracked-files=normal']).strip()
        require(revision == lock['revision'] and not status, 'SDK requires exact clean pinned revision')
        require(digest(sdk / lock['canonical_path']) == lock['sha256'], 'Canonical TypeScript hash mismatch')
        require(digest(sdk / 'sdk-manifest.json') == lock['manifest_sha256'], 'SDK manifest hash mismatch')
        manifest = read_json(sdk / 'sdk-manifest.json')
        require(manifest['version'] == lock['package_version'], 'SDK package version mismatch')
        profile = lock['profile']
        require(manifest['profiles'][profile['name']] == {
            'language': 'luau', 'declaration': profile['declaration_path'], 'guide': profile['guide_path'],
            'availability': 'native-bound-host', 'compatibility': 'alpha'}, 'SDK manifest profile mismatch')
        for kind in ('declaration', 'guide'):
            path, expected = profile[kind + '_path'], profile[kind + '_sha256']
            require(manifest['files'][path] == expected and digest(sdk / path) == expected,
                    'SDK profile ' + kind + ' hash mismatch')
    print('PASS: pinned SDK compatibility provenance')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sdk-source', default='')
    verify(parser.parse_args().sdk_source)
