import json
import contextlib, datetime, hashlib, os, pathlib, plistlib, re, secrets, shlex, shutil, subprocess, tempfile, zipfile

def stop(message):
    print('FAIL: ' + message, flush=True)
    raise SystemExit(1)

def checked(command, message):
    result = subprocess.run(command, capture_output=True)
    if result.returncode:
        stop(message)
    return result.stdout

def ptt_state(entitlements):
    if 'com.apple.developer.push-to-talk' not in entitlements:
        return 'missing'
    return 'present' if entitlements['com.apple.developer.push-to-talk'] is True else 'unexpected'

def apns_state(entitlements):
    value = entitlements.get('aps-environment')
    if value is None:
        return 'missing'
    return value if value in ('production', 'development') else 'unexpected'

def id_state(entitlements, key, expected):
    if key not in entitlements:
        return 'missing'
    return 'match' if entitlements[key] == expected else 'mismatch'

def profile_type(profile):
    entitlements = profile.get('Entitlements', {})
    debug = entitlements.get('get-task-allow')
    devices = profile.get('ProvisionedDevices')
    if profile.get('ProvisionsAllDevices') is True:
        return 'enterprise'
    if devices:
        if debug is True:
            return 'development'
        if debug is False:
            return 'adhoc'
        return 'unknown'
    if debug is False and entitlements.get('beta-reports-active') is True:
        return 'app-store'
    return 'unknown'

def expiry_state(profile):
    expiry = profile.get('ExpirationDate')
    if not isinstance(expiry, datetime.datetime):
        return 'unknown'
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=datetime.timezone.utc)
    return 'current' if expiry > datetime.datetime.now(datetime.timezone.utc) else 'expired'

def safe_diagnostic(signed, profile, team, bundle):
    permitted = profile.get('Entitlements', {})
    return {
        'SIGNED_APP_PTT_ENTITLEMENT': ptt_state(signed),
        'PROFILE_PTT_ENTITLEMENT': ptt_state(permitted),
        'SIGNED_APP_APNS': apns_state(signed),
        'PROFILE_APNS': apns_state(permitted),
        'SIGNED_APP_APP_ID': id_state(signed, 'application-identifier', team + '.' + bundle),
        'PROFILE_APP_ID': id_state(permitted, 'application-identifier', team + '.' + bundle),
        'SIGNED_APP_TEAM': id_state(signed, 'com.apple.developer.team-identifier', team),
        'PROFILE_TEAM': id_state(permitted, 'com.apple.developer.team-identifier', team),
        'PROFILE_TEAM_METADATA': 'match' if profile.get('TeamIdentifier') == [team] else 'mismatch',
        'SIGNED_APP_NON_DEBUG': 'yes' if signed.get('get-task-allow') is False else 'no',
        'PROFILE_NON_DEBUG': 'yes' if permitted.get('get-task-allow') is False else 'no',
        'PROFILE_TYPE': profile_type(profile),
        'PROFILE_EXPIRY': expiry_state(profile),
    }

@contextlib.contextmanager
def ephemeral_profiles():
    roots = [
        pathlib.Path.home() / 'Library/MobileDevice/Provisioning Profiles',
        pathlib.Path.home() / 'Library/Developer/Xcode/UserData/Provisioning Profiles',
    ]
    before = {p for root in roots if root.exists() for p in root.iterdir() if p.is_file()}
    try:
        yield
    finally:
        for root in roots:
            if root.exists():
                for path in root.iterdir():
                    if path.is_file() and path not in before:
                        path.unlink()
        print('TEMPORARY_SIGNING_PROFILES_CLEANUP=pass', flush=True)

@contextlib.contextmanager
def ephemeral_keychain(private):
    # Only local, disposable runner resources; no Apple certificates are revoked.
    keychain = private / 'archive-signing.keychain-db'
    original_default = checked(['security', 'default-keychain', '-d', 'user'], 'Cannot inspect local default keychain.').decode().strip().strip('"')
    original_list = shlex.split(checked(['security', 'list-keychains', '-d', 'user'], 'Cannot inspect local keychain search list.').decode())
    password = secrets.token_urlsafe(32)
    created = False
    try:
        checked(['security', 'create-keychain', '-p', password, str(keychain)], 'Cannot create temporary signing keychain.')
        created = True
        checked(['security', 'set-keychain-settings', '-lut', '1800', str(keychain)], 'Cannot configure temporary signing keychain.')
        checked(['security', 'unlock-keychain', '-p', password, str(keychain)], 'Cannot unlock temporary signing keychain.')
        checked(['security', 'list-keychains', '-d', 'user', '-s', str(keychain), *original_list], 'Cannot set temporary keychain search list.')
        checked(['security', 'default-keychain', '-d', 'user', '-s', str(keychain)], 'Cannot set temporary default keychain.')
        yield
    finally:
        restored_default = subprocess.run(['security', 'default-keychain', '-d', 'user', '-s', original_default], capture_output=True).returncode == 0
        restored_list = subprocess.run(['security', 'list-keychains', '-d', 'user', '-s', *original_list], capture_output=True).returncode == 0
        removed = not created or subprocess.run(['security', 'delete-keychain', str(keychain)], capture_output=True).returncode == 0
        if not (restored_default and restored_list and removed):
            stop('Temporary keychain cleanup or restoration failed.')
        print('TEMPORARY_KEYCHAIN_CLEANUP=pass', flush=True)

try:
    if os.environ.get('GITHUB_RUN_ATTEMPT') != '1':
        stop('Build 17 reruns are prohibited.')
    team = os.environ['APPLE_TEAM_ID']
    key_id = os.environ['ASC_KEY_ID']
    issuer = os.environ['ASC_ISSUER_ID']
    pem = os.environ.pop('ASC_API_KEY_P8')
    if not re.fullmatch(r'[A-Z0-9]{10}', team) or not re.fullmatch(r'[A-Z0-9]{10}', key_id):
        stop('Invalid signing identifier format.')
    if not re.fullmatch(r'[a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}', issuer):
        stop('Invalid issuer identifier format.')
    if not pem.strip().startswith('-----BEGIN PRIVATE KEY-----'):
        stop('Private-key format is invalid.')
    probe = pathlib.Path(os.environ['RUNNER_TEMP']) / 'slime-talk-signing-probe'
    probe.mkdir(parents=True, exist_ok=True)
    archive = probe / 'SlimeTalk.xcarchive'
    with ephemeral_profiles(), tempfile.TemporaryDirectory(prefix='apple-signing-', dir=probe) as private_dir:
        private = pathlib.Path(private_dir)
        key_path = private / 'AuthKey.p8'
        key_path.write_text(pem.strip() + '\n')
        del pem
        options = private / 'ExportOptions.plist'
        options.write_bytes(plistlib.dumps({
            'method': 'app-store-connect', 'destination': 'export',
            'signingStyle': 'automatic', 'teamID': team,
            'manageAppVersionAndBuildNumber': False, 'uploadSymbols': False,
        }))

        # Standard automatic signing with the existing App ID/team/API key.
        # Signing output is captured privately; only fixed status labels escape.
        archive_log = private / 'signed-archive.log'
        profile_roots = [
            pathlib.Path.home() / 'Library/MobileDevice/Provisioning Profiles',
            pathlib.Path.home() / 'Library/Developer/Xcode/UserData/Provisioning Profiles',
        ]
        profiles_before = {p for root in profile_roots if root.exists() for p in root.iterdir() if p.is_file()}
        try:
            with ephemeral_keychain(private):
                with archive_log.open('wb') as log:
                    result = subprocess.run([
                        'xcodebuild', 'archive',
                        '-project', 'ios/SlimeTalk.xcodeproj', '-scheme', 'SlimeTalk',
                        '-configuration', 'Release', '-destination', 'generic/platform=iOS',
                        '-archivePath', str(archive), '-derivedDataPath', str(probe / 'DerivedData'),
                        'CODE_SIGNING_ALLOWED=YES', 'CODE_SIGN_STYLE=Automatic',
                        'PRODUCT_BUNDLE_IDENTIFIER=ai.slimy.slimetalk.feasibility',
                        'DEVELOPMENT_TEAM=' + team,
                        'CURRENT_PROJECT_VERSION=17',
                        '-allowProvisioningUpdates', '-authenticationKeyPath', str(key_path),
                        '-authenticationKeyID', key_id, '-authenticationKeyIssuerID', issuer,
                    ], stdout=log, stderr=subprocess.STDOUT, timeout=600)
                if result.returncode:
                    diagnostic = archive_log.read_text(errors='replace').lower()
                    for needle, label in [
                        ('no signing certificate', 'no-usable-signing-certificate'),
                        ('no profiles for', 'no-matching-profile'),
                        ('no devices', 'no-registered-development-devices'),
                        ('has no devices', 'no-registered-development-devices'),
                        ('does not support', 'unsupported-capability-or-configuration'),
                        ("doesn't support", 'unsupported-capability-or-configuration'),
                        ("doesn't include", 'profile-missing-required-item'),
                        ('no accounts', 'account-access-unavailable'),
                        ('not permitted', 'signing-operation-rejected'),
                        ('user interaction is not allowed', 'keychain-interaction-required'),
                    ]:
                        if needle in diagnostic:
                            print('ARCHIVE_DIAGNOSTIC=' + label, flush=True)
                    stop('Automatic signed archive failed; sensitive details suppressed.')
                archive_app = archive / 'Products/Applications/SlimeTalk.app'
                checked(['codesign', '--verify', '--deep', '--strict', str(archive_app)],
                        'Archive application signature verification failed.')
                archive_signed = plistlib.loads(checked(['codesign', '-d', '--entitlements', ':-', str(archive_app)],
                        'Cannot read archive application entitlements.'))
                archive_profile = plistlib.loads(checked(['security', 'cms', '-D', '-i', str(archive_app / 'embedded.mobileprovision')],
                        'Cannot decode archive profile.'))
                archive_metadata = safe_diagnostic(archive_signed, archive_profile, team, 'ai.slimy.slimetalk.feasibility')
                print('ARCHIVE_APP_PTT=' + archive_metadata['SIGNED_APP_PTT_ENTITLEMENT'], flush=True)
                print('ARCHIVE_PROFILE_PTT=' + archive_metadata['PROFILE_PTT_ENTITLEMENT'], flush=True)
                print('ARCHIVE_APNS=' + archive_metadata['SIGNED_APP_APNS'], flush=True)
                print('ARCHIVE_PROFILE_APNS=' + archive_metadata['PROFILE_APNS'], flush=True)
                for field in ('SIGNED_APP_APP_ID', 'PROFILE_APP_ID', 'SIGNED_APP_TEAM', 'PROFILE_TEAM', 'PROFILE_TEAM_METADATA', 'PROFILE_TYPE', 'PROFILE_EXPIRY'):
                    print('ARCHIVE_' + field + '=' + archive_metadata[field], flush=True)
                print('ARCHIVE_SIGNATURE=valid', flush=True)
                if archive_metadata['PROFILE_PTT_ENTITLEMENT'] != 'present':
                    stop('Apple-generated archive profile excludes required PushToTalk; stop for provisioning review.')
                if archive_metadata['SIGNED_APP_PTT_ENTITLEMENT'] != 'present':
                    stop('Signed archive application lacks required PushToTalk.')
                if any(archive_metadata[field] != 'match' for field in ('SIGNED_APP_APP_ID', 'PROFILE_APP_ID', 'SIGNED_APP_TEAM', 'PROFILE_TEAM', 'PROFILE_TEAM_METADATA')):
                    stop('Archive app or profile identifiers do not match.')
                if archive_metadata['PROFILE_EXPIRY'] != 'current':
                    stop('Archive profile is not current.')
                if archive_metadata['SIGNED_APP_APNS'] not in ('development', 'production') or archive_metadata['SIGNED_APP_APNS'] != archive_metadata['PROFILE_APNS']:
                    stop('Archive APNs entitlements are missing or inconsistent.')
        finally:
            for root in profile_roots:
                if root.exists():
                    for profile_path in root.iterdir():
                        if profile_path.is_file() and profile_path not in profiles_before:
                            profile_path.unlink()
            print('TEMPORARY_ARCHIVE_PROFILES_CLEANUP=pass', flush=True)
        export = private / 'export'
        # Raw Xcode distribution output stays private and is never uploaded.
        log_path = private / 'export.log'
        with log_path.open('wb') as log:
            result = subprocess.run([
                'xcodebuild', '-exportArchive', '-archivePath', str(archive),
                '-exportPath', str(export), '-exportOptionsPlist', str(options),
                '-allowProvisioningUpdates', '-authenticationKeyPath', str(key_path),
                '-authenticationKeyID', key_id, '-authenticationKeyIssuerID', issuer,
            ], stdout=log, stderr=subprocess.STDOUT, timeout=600)
        if result.returncode:
            diagnostic = log_path.read_text(errors='replace').lower()
            for needle, label in [
                ('cloud signing permission', 'Cloud signing permission was rejected.'),
                ('no signing certificate', 'Xcode reports no usable signing certificate.'),
                ('no profiles for', 'Xcode reports no matching provisioning profile.'),
                ('does not support', 'Xcode reports an unsupported capability or configuration.'),
                ('doesn\'t support', 'Xcode reports an unsupported capability or configuration.'),
                ('no accounts', 'Xcode reports that account access is unavailable.'),
                ('not permitted', 'Apple rejected a requested signing operation.'),
                ('requires a provisioning profile', 'A provisioning profile is required.'),
            ]:
                if needle in diagnostic:
                    print('DIAGNOSTIC: ' + label, flush=True)
            stop('Cloud export failed; raw distribution logs and credentials are suppressed.')
        ipas = list(export.glob('*.ipa'))
        if len(ipas) != 1:
            stop('Expected exactly one exported IPA.')
        extracted = private / 'unpacked'
        with zipfile.ZipFile(ipas[0]) as package:
            for name in package.namelist():
                path = pathlib.PurePosixPath(name)
                if path.is_absolute() or '..' in path.parts:
                    stop('Unexpected package path.')
            package.extractall(extracted)
        app = extracted / 'Payload' / 'SlimeTalk.app'
        checked(['codesign', '--verify', '--deep', '--strict', str(app)],
                'Exported application signature verification failed.')
        signed = plistlib.loads(checked(['codesign', '-d', '--entitlements', ':-', str(app)],
                'Cannot read signed application entitlements.'))
        profile = plistlib.loads(checked(['security', 'cms', '-D', '-i', str(app / 'embedded.mobileprovision')],
                'Cannot decode the embedded provisioning profile.'))
        info = plistlib.loads((app / 'Info.plist').read_bytes())
        bundle = 'ai.slimy.slimetalk.feasibility'
        for field, state in safe_diagnostic(signed, profile, team, bundle).items():
            print(field + '=' + state, flush=True)
        print('SIGNATURE=valid', flush=True)
        print('BUNDLE_ID=' + ('match' if info.get('CFBundleIdentifier') == bundle else 'mismatch'), flush=True)
        print('PTT_BACKGROUND_MODE=' + ('present' if info.get('UIBackgroundModes') == ['push-to-talk'] else 'unexpected'), flush=True)
        if profile.get('TeamIdentifier') != [team]:
            stop('Embedded profile team metadata does not match.')
        if info.get('CFBundleIdentifier') != bundle or info.get('UIBackgroundModes') != ['push-to-talk']:
            stop('Unexpected bundle ID or background modes.')
        for entitlements in (signed, profile.get('Entitlements', {})):
            if entitlements.get('com.apple.developer.push-to-talk') is not True:
                stop('PushToTalk entitlement is missing or not permitted; stop for provisioning review.')
            if entitlements.get('aps-environment') != 'production':
                stop('Production APNs entitlement is missing; stop for provisioning review.')
            if entitlements.get('application-identifier') != team + '.' + bundle:
                stop('Unexpected signed application identifier.')
            if entitlements.get('com.apple.developer.team-identifier') != team:
                stop('Unexpected signing team.')
            if entitlements.get('get-task-allow') is not False:
                stop('Unexpected debug entitlement in distribution output.')
        if profile.get('ProvisionedDevices') or profile.get('ProvisionsAllDevices'):
            stop('Export is not an App Store distribution profile.')
        if profile.get('Entitlements', {}).get('beta-reports-active') is not True:
            stop('Profile does not indicate App Store beta distribution.')
        expiry = profile.get('ExpirationDate')
        if not isinstance(expiry, datetime.datetime) or expiry <= datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None):
            stop('Provisioning profile is expired or has no valid expiration.')
        print('PASS: exported distribution application signature verifies.')
        print('PASS: signed app and profile both permit PushToTalk and production APNs for the exact feasibility App ID.')
        print('PASS: non-debug App Store distribution profile is current.')
        if info.get('CFBundleShortVersionString') != '0.1.0' or str(info.get('CFBundleVersion')) != '17':
            stop('Exact version/build verification failed.')
        print('IPA_SHA256=' + hashlib.sha256(ipas[0].read_bytes()).hexdigest())
        if os.environ.get('UPLOAD_TESTFLIGHT') == 'true':
            if info.get('SLIMEFeasibilityRuntime') != '003':
                stop('Only the actual runtime candidate may be uploaded.')
            # altool reads the same authorized key from this private directory.
            upload_key = private / ('AuthKey_' + key_id + '.p8')
            key_path.rename(upload_key)
            upload_env = dict(os.environ, API_PRIVATE_KEYS_DIR=str(private))
            upload_log = private / 'upload.log'
            with upload_log.open('wb') as log:
                result = subprocess.run([
                    'xcrun', 'altool', '--upload-app', '-f', str(ipas[0]),
                    '--type', 'ios', '--apiKey', key_id, '--apiIssuer', issuer,
                    '--output-format', 'json',
                ], stdout=log, stderr=subprocess.STDOUT, env=upload_env, timeout=600)
            # Only an explicitly named request identifier may escape raw output.
            raw = upload_log.read_text(errors='replace')
            request_ids = set()
            try:
                payload = json.loads(raw)
            except ValueError:
                payload = None
            def find_request_id(value):
                if isinstance(value, dict):
                    for name, item in value.items():
                        if name.lower().replace('-', '').replace('_', '') in ('requestid', 'requestuuid'):
                            if isinstance(item, str) and re.fullmatch(r'[a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}', item):
                                request_ids.add(item)
                        find_request_id(item)
                elif isinstance(value, list):
                    for item in value:
                        find_request_id(item)
            find_request_id(payload)
            for match in re.finditer(r'(?im)^\s*Request(?:UUID|[-_ ]?ID)\s*[:=]\s*([a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12})\s*$', raw):
                request_ids.add(match.group(1))
            print('UPLOAD_REQUEST_ID=' + (next(iter(request_ids)) if len(request_ids) == 1 else 'not_returned'), flush=True)
            print('UPLOAD_TIMESTAMP_UTC=' + datetime.datetime.now(datetime.timezone.utc).isoformat(), flush=True)
            print('UPLOAD_TRANSPORT_RESULT=' + ('accepted' if result.returncode == 0 else 'failed'), flush=True)
            if any(word in raw.lower() for word in ('export compliance', 'encryption', 'agreement', 'attestation', 'content rights', 'billing')):
                stop('OWNER_ATTESTATION_REVIEW_REQUIRED; stop and inspect exact question privately in Apple UI.')
            del raw, payload
            # Raw upload output is never logged; processing is checked separately.
            if result.returncode:
                diagnostic = upload_log.read_text(errors='replace').lower()
                for needle, label in [
                    ('encryption', 'owner-export-compliance-review-required'),
                    ('agreement', 'owner-agreement-review-required'),
                    ('icon', 'app-icon-validation'),
                    ('version', 'build-version-validation'),
                    ('authentication', 'upload-authentication-failure'),
                ]:
                    if needle in diagnostic:
                        print('UPLOAD_DIAGNOSTIC=' + label, flush=True)
                stop('TestFlight upload failed; raw upload output suppressed.')
            print('TESTFLIGHT_UPLOAD_COMMAND=accepted', flush=True)
            print('TESTFLIGHT_PROCESSING=not-yet-verified', flush=True)
            print('IOS_VERSION=' + str(info.get('CFBundleShortVersionString')), flush=True)
            print('IOS_BUILD=' + str(info.get('CFBundleVersion')), flush=True)
            print('Owner export-compliance answers were NOT supplied.', flush=True)
        else:
            print('TESTFLIGHT_UPLOAD=not-requested', flush=True)
        print('Physical-device F1-F7 are NOT TESTED.')
except SystemExit:
    raise
except subprocess.TimeoutExpired:
    stop('Cloud export timed out; details suppressed.')
except Exception:
    stop('Signing verification did not complete; sensitive error details suppressed.')
