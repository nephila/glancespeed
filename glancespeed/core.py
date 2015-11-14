import copy, json, six, subprocess


def _get_result_json(host, strategy):
    cmd = 'psi {0} --strategy={1} --format=json --threshold=1'.format(host, strategy)
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result_json = ''
    for line in result.stdout:
        result_json += line
    return json.loads(result_json)


def _get_results(host):
    desktop_json = _get_result_json(host, 'desktop')
    mobile_json = _get_result_json(host, 'mobile')
    result_json = {
        'desktop': desktop_json,
        'mobile' : mobile_json
    }
    return result_json


def _calculate_diff(new_value, old_value):
    if isinstance(new_value, (int, float)) and isinstance(old_value, (int, float)):
        return new_value - old_value
    else:
        return new_value


def _create_diff(new_result, old_result, diff_result={}):
    if not diff_result:
        diff_result = copy.deepcopy(new_result)
    for k, v in six.iteritems(diff_result):
        if isinstance(v, dict):
            diff_result[k] = _create_diff(new_result[k], old_result[k], diff_result[k])
        else:
            diff_result[k] = _calculate_diff(new_result[k], old_result[k])
    return diff_result


def _diff_results(new_result, old_result):
    if not old_result:
        old_result = new_result
    return _create_diff(new_result, old_result)


def glancespeed(host):
    filename= '.glancespeed'
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
