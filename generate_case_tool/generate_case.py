import os
import sys
from datetime import datetime
from fuzzywuzzy import fuzz
import xml.etree.ElementTree as ET
from jinja2 import Environment, FileSystemLoader
import argparse


def fix_path():
    """
    add ATOM root path to sys.path so TestRailAPI/pub could be imported.
    """
    abs_path = os.path.abspath(__file__)
    abs_folder1 = os.path.dirname(abs_path)
    abs_folder2 = os.path.dirname(abs_folder1)
    atom_path = os.path.join(abs_folder2, os.path.pardir)
    sys.path.append(os.path.abspath(atom_path))
    print(sys.path)


fix_path()
from utilities.TestRailAPI.TRClient import TestRailClient
from pub.Const import FORNAXKEPLER, FORNAXKOSMOS

# constants
PROJECT_FFV = 1
TEST_SUITE_ATOM = 13
TEST_SUITE_UEFI = 9
TEST_SUITE_BMC = 2

dict_platform = {
    1: EUROPA,
    2: OBERON,
    3: HYPERION,
    4: LUNA,
    5: WARTHOG,
    6: BEACHCOMBERFC,
    7: EUROPA1U,
    8: 'NONE',
    9: 'NONE',
    10: BANSHEE,
    11: 'NONE',
    12: WARNADO,
    13: ENTERPRISE,
    14: 'NONE',
    15: WARNADOEX,
    16: 'NONE',
    17: RIPTIDE,
    18: BOLERO,
    19: ENTRY,
    20: FORNAXKEPLER,
    21: FORNAXKOSMOS,
}

case_info_dict = {}


def generate_case(caseid, username='who', path=''):
    global case_info_dict
    case_info_dict['writer'] = username
    get_case_info_from_testrail(caseid)
    generate_case_file(path)


def get_case_info_from_testrail(caseid):
    global case_info_dict
    testrail = TestRailClient()
    case_filter = '&suite_id={}'.format(TEST_SUITE_UEFI)
    ret1 = testrail.get_cases(PROJECT_FFV, case_filter)
    case_filter = '&suite_id={}'.format(TEST_SUITE_BMC)
    ret2 = testrail.get_cases(PROJECT_FFV, case_filter)

    caseall = ret1 + ret2
    dstcase_stepall = ''
    for case in caseall:
        case_tr_id = case['id']

        if case_tr_id == caseid:
            case_platform_id = case['custom_ffvplatform']
            case_platform = [dict_platform[i] for i in case_platform_id]
            print(case)
            step_list = case.get('custom_steps_separated')
            print(step_list)

            file_title = case.get('title')
            if case in ret1:
                file_new = 'C' + str(case_tr_id) + '_uefi_' + file_title.title().replace(' ', '')
            else:
                file_new = 'C' + str(case_tr_id) + '_bmc_' + file_title.title().replace(' ', '')
            file_new = file_new.replace('/', '')

            created_time = str(datetime.now())

            case_info_dict['title'] = file_title
            case_info_dict['time_now'] = created_time
            case_info_dict['file_name'] = file_new
            case_info_dict['support_platform'] = case_platform
            case_info_dict['preconditions'] = case.get('custom_preconds')
            case_info_dict['steps'] = []
            case_info_dict['excepts'] = []

            if not step_list:
                break
            for step in step_list:
                dstcase_stepall += step.get('content')
                content = step.get('content').replace('\n', '-->')
                case_info_dict['steps'].append(content.replace('"', ' '))
                expected = step.get('expected').replace('\n', '-->')
                case_info_dict['excepts'].append(expected.replace('"', ' '))
            break
    if case['id'] != caseid:
        raise Exception("can't find case {} in testrail page uefi/bmc :please check".format(caseid))
    case_info_dict['stepnum'] = len(case_info_dict['steps'])

    case_filter = '&suite_id={}'.format(TEST_SUITE_ATOM)
    casemsg = testrail.get_cases(PROJECT_FFV, case_filter)
    scorelist = [0, 0]
    pricase = [0, 0]
    for case in casemsg:
        dstcase_step = ''
        case_tr_id = case['id']
        if case_tr_id == caseid:
            continue
        step_list = case.get('custom_steps_separated')
        if step_list:
            for step in step_list:
                dstcase_step += step.get('content')

            score = fuzz.ratio(dstcase_stepall, dstcase_step)

            if score > scorelist[0]:
                tmp = scorelist[0]
                scorelist[0] = score
                scorelist[1] = tmp
                tmp = pricase[0]
                pricase[0] = case_tr_id
                pricase[1] = tmp
            elif score > scorelist[1]:
                scorelist[1] = score
                pricase[1] = case_tr_id
            else:
                pass
    case_info_dict['pricase'] = pricase
    print(scorelist)
    print(pricase)


PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def generate_case_file(path=''):
    tree = ET.parse('templates/case_config_template.xml')
    root = tree.getroot()
    root.find('platform').text = ', '.join(case_info_dict['support_platform'])
    tree.write(path + case_info_dict['file_name'] + '.xml')

    fname = path + case_info_dict['file_name'] + '.py'

    with open(fname, 'w+') as f:
        file_case = render_template('jinja2_template.py', case_info_dict).encode('ascii', 'ignore').decode('ascii')
        f.write(file_case)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='automate generate test case')

    parser.add_argument("-c", "--caseid", type=int, \
                       help="case id no char 'C'")

    parser.add_argument("-p", "--gpath", type=str, \
                        help="the  path case will be generated")

    commandList = parser.parse_args()
    if not commandList.caseid:
        raise Exception("Error: no caseid- please enter case number")
    if commandList.gpath:
        if not os.path.exists(commandList.gpath):
            raise Exception("path not exist")
    else:
        commandList.gpath = ''
    if sys.version_info[0] == 2:
        import commands
        ret_tup = commands.getstatusoutput("git config --get user.email")
    else:
        import subprocess
        ret_tup = subprocess.getstatusoutput("git config --get user.email")
    generate_case(commandList.caseid, ret_tup[1], commandList.gpath)
