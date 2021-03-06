from __future__ import print_function

import copy, json, os, re, six, subprocess

from termcolor import colored


POSITIVES = ['Score']

NEGATIVES = [
    'cssResponseBytes', 'htmlResponseBytes', 'imageResponseBytes',
    'javascriptResponseBytes', 'numberCssResources', 'numberHosts',
    'numberJsResources', 'numberResources', 'numberStaticResources',
    'otherResponseBytes', 'totalRequestBytes',
]

STATISTICS = {
    'cssResponseBytes': 'CSS size',
    'htmlResponseBytes': 'HTML size',
    'imageResponseBytes': 'Image size',
    'javascriptResponseBytes': 'JavaScript size',
    'numberCssResources': 'CSS resources ',
    'numberHosts': 'Hosts',
    'numberJsResources': 'JS resources',
    'numberResources': 'Resources',
    'numberStaticResources': 'Static resources',
    'otherResponseBytes': 'Other size ',
    'totalRequestBytes': 'Total size',
}

DIMENSION_REGEXP = '([0-9]+(\.[0-9]+)?)\s([k|M]?B)'


class GlanceSpeedException(Exception):
    pass

def _get_result_json(host, strategy):
    log_file = open('.glancespeed/logs', 'w')
    cmd = 'psi {0} --strategy={1} --format=json --threshold=1'.format(host, strategy)
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=log_file)
    result_json = ''
    for line in result.stdout:
        result_json += line
    try:
        return json.loads(result_json)
    except ValueError:
        raise GlanceSpeedException(result_json)
    finally:
        log_file.close()


def _get_results(host):
    desktop_json = _get_result_json(host, 'desktop')
    mobile_json = _get_result_json(host, 'mobile')
    result_json = {
        'desktop': desktop_json,
        'mobile' : mobile_json
    }
    return result_json


def _diff_dimensions(key, new_value, old_value):

    um_mul = {
        'B': 1,
        'kB': 1000,
        'MB': 1000 * 1000
    }

    match = re.search(DIMENSION_REGEXP, new_value)
    new_value = float(match.group(1))
    new_um = match.group(3)
    _trans_new_value = new_value * um_mul[new_um]
    match = re.search(DIMENSION_REGEXP, old_value)
    old_value = float(match.group(1))
    old_um = match.group(3)
    _trans_old_value = old_value * um_mul[old_um]
    _new_value, _old_value = (_trans_new_value, _trans_old_value) if _trans_new_value > _trans_old_value else (_trans_old_value, _trans_new_value)

    final_value = _new_value - _old_value
    final_um = new_um
    if new_um != old_um:
        final_um = new_um if um_mul[new_um] > um_mul[old_um] else old_um
    final_value = final_value / um_mul[final_um]

    diff = {
        'new': '{0} {1}'.format(new_value, new_um),
        'sign': '-' if _trans_new_value < _trans_old_value else '+',
        'diff': '{0} {1}'.format(final_value, final_um),
        'status': _check_status(key, new_value, old_value)
    }
    return diff


def _is_dimension(value):
    if not isinstance(value, six.string_types):
        return False
    match = re.search(DIMENSION_REGEXP, value)
    if match:
        return True
    return False


def _check_status(key, new_value, old_value):
    if (new_value == old_value):
        return 'OK'
    if key in POSITIVES and new_value > old_value:
        return 'OK'
    elif key in NEGATIVES and new_value < old_value:
        return 'OK'
    else:
        return 'BAD'

def _calculate_diff(key, new_value, old_value):
    diff = new_value
    if _is_dimension(new_value) and _is_dimension(old_value):
        diff = _diff_dimensions(key, new_value, old_value)
    if isinstance(new_value, (int, float)) and isinstance(old_value, (int, float)):
        _new_value, _old_value = (new_value, old_value) if new_value > old_value else (old_value, new_value)
        diff = {
            'new': new_value,
            'sign': '-' if new_value < old_value else '+',
            'diff': _new_value - _old_value,
            'status': _check_status(key, new_value, old_value)
        }
    return diff


def _create_diff(new_result, old_result, diff_result={}):
    if not diff_result:
        diff_result = copy.deepcopy(new_result)
    for k, v in six.iteritems(diff_result):
        if isinstance(v, dict):
            diff_result[k] = _create_diff(new_result[k], old_result[k], diff_result[k])
        else:
            diff_result[k] = _calculate_diff(k, new_result[k], old_result[k])
    return diff_result


def _diff_results(new_result, old_result):
    if not old_result:
        old_result = new_result
    return _create_diff(new_result, old_result)


def _normalize_host_name(host):
    return host.strip('/').replace('/', '-')


def _glance_speed_diff(host):
    directory = '.glancespeed'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename= os.path.join(directory, _normalize_host_name(host))
    new_result = _get_results(host)
    old_result = None
    try:
        old_result = open(filename, 'r').read()
        old_result = json.loads(old_result)
    except IOError as e:
        pass
    f = open(filename, 'w')
    diff = _diff_results(new_result, old_result)
    f.write(json.dumps(new_result, indent=4, sort_keys=True))
    f.close()
    return diff


def _print_score(diff):
    colored_output = colored(
        '{0}/100 ({1}{2})'.format(
            diff['new'], diff['sign'],diff['diff']
        ), 'green' if diff['status'] == 'OK' else 'red',
        attrs=['bold'])
    print(colored_output)


def _print_diff(diff, long_description):
    colored_output = colored(
        '{0}{1}| {2} ({3}{4})'.format(
            long_description, ' ' * (39 - len(long_description)),
            diff['new'], diff['sign'],
            diff['diff']
        ), 'green' if diff['status'] == 'OK' else 'red')
    print(colored_output)


def _print_strategy(strategy, diff):
    overview = diff[strategy]['overview']
    statistics = diff[strategy]['statistics']
    _print_score(overview['Score'])
    for k, v in six.iteritems(STATISTICS):
        if k in statistics:
            _print_diff(statistics[k], v)


def glancespeed(host):
    try:
        diff = _glance_speed_diff(host)
    except GlanceSpeedException as ex:
        print (colored('Error executing psi:', 'red', attrs=['bold']))
        print (open('.glancespeed/logs', 'r').read())
        return
    print (colored('\nMobile', 'white', attrs=['bold']), end=' ')
    _print_strategy('mobile', diff)
    print (colored('\nDesktop', 'white', attrs=['bold']), end=' ')
    _print_strategy('desktop', diff)
