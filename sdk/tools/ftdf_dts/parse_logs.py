import sys
import os
import re
import argparse
from datetime import datetime
from collections import defaultdict
from time import sleep

STATE_SCRIPT = 0
STATE_RESULT = 1

rot = '|/-\|/-\\'
roti = 0
script_results = []
dups = []
missed = []


def waiting(msg=""):
    global roti
    print "%c %s\r" % (rot[roti], msg),
    sys.stdout.flush()
    roti = (roti + 1) % len(rot)


def parse_args():
    parser = argparse.ArgumentParser(
        description='This script parses an FTDF DTS log file and produces a summary of the results. The exit code depends on the options used (Default: 0)')
    parser.add_argument('log_file', help='The DTS log file to parse')
    parser.add_argument("-s", "--strict",
                        help="strict mode; all scripts must pass on all runs, to consider the test successful.",
                        action="store_true")
    parser.add_argument("-p", "--percent", type=int,
                        help="Percentage mode. Defines the percentage (%%) of passed scripts to consider the test passed. If -m is also selected, all scripts must additionally pass at least MINPASS times.",
                        action="store")
    parser.add_argument("-m", "--minpass", type=int,
                        help="Minimum number of passes for all scripts. That is, each script must pass at least MINPASS times to consider the test successful. Can be combined with -p.",
                        action="store")
    parser.add_argument("-g", "--group", help="Print scripts grouped by number of passes.",
                        action="store_true")

    parser.add_argument("-i", "--iterations", type=int,help="How many times each test has run", action="store")

    args = parser.parse_args()
    if args.strict and args.percent:
        print "Error: Cannot use -s and -p simultaneously"
        exit(1)
    if args.percent and (args.percent < 0 or args.percent > 100):
        print "Error: PERCENT must be in [0, 100]"
        exit(1)
    if args.minpass and args.minpass < 0:
        print "Error: MINPASS must be >= 0"
        exit(1)
    if args.minpass and args.iterations:
        if args.minpass > args.iterations:
            print "Error: MINPASS must be <= ITERATIONS"
            exit(1)
    return args


def parse_time(line):
    m = re.search('(.*?),.*$', line)
    o = None
    if m:
        ts = m.group(1)
        try:
            o = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
        except:
            pass
    return o


def get_time_diff_in_secs(start_time, line):
    end_time = parse_time(line)
    if start_time and end_time:
        d = end_time - start_time
        return d.total_seconds()
    else:
        return 0


def parse_log(fname):
    global script_results, dups, missed
    log = ""
    state = STATE_SCRIPT
    script = ""
    prev_script = ""
    f = open(sys.argv[1])
    start_time = None
    bytes_nr = 0
    total_size = os.path.getsize(sys.argv[1])
    prev_p = -1
    for l in f:
        p = int((100.0 * bytes_nr / total_size))
        if p != prev_p:
            prev_p = p
            print "Parsing log file: %d%%\r" % p,
            sys.stdout.flush()
        m = re.search('Executing script: (.*)$', l)
        if m:
            s = m.group(1).strip()
            if state == STATE_RESULT:
                missed.append(script)
            state = STATE_RESULT
            script = s
            log = ""
            start_time = parse_time(l)

        log += l
        bytes_nr += len(l)
        m = re.search('SCRIPT: PASSED', l)
        if m:
            if state == STATE_RESULT:
                script_results.append((script, True, "",
                                       get_time_diff_in_secs(start_time, l)))
                prev_script = script
                script = ""
                state = STATE_SCRIPT
            else:
                dups.append(prev_script)
        m = re.search('SCRIPT: FAILED', l)
        if m:
            if state == STATE_RESULT:
                script_results.append((script, False, log,
                                       get_time_diff_in_secs(start_time, l)))
                prev_script = script
                script = ""
                state = STATE_SCRIPT
            else:
                dups.append(prev_script)


''' Parses the parsed script results and returns:
	- max_passes: How many passes/iterations have run per script (max)
   	- total_runs: Total number of runs for all scripts 
 	- total_passes: Total successful runs for all scripts
 	- scripts_d: A dict containing stats per script:
		[script name]: {
			# Cumulative stats for all iterations for this script
			'totals' : [<Passed iterations>, <Failed iterations>],

			# Each entry in this list is an iteration (dict):
			'iters' : [ <iter 1 dict>, <iter 2 dict> .. ]
		}
		where: <iter 1 dict> : {
			'time' : The iteration elapsed time in secs
			'result' : The iteration result (True/False)
			'log': When result is False, this is the iteration log,
				otherwise, an empty string
		}
'''


def process_results():
    # Count the passes and failures for each script
    total_runs = 0
    total_passes = 0
    scripts_d = {}
    max_passes = 0

    print "                                   \r",

    for (script, result, log, duration) in script_results:
        waiting("Processing results...")
        if script not in scripts_d:
            scripts_d[script] = {'totals': [0, 0], 'iters': []}
        counts = scripts_d[script]['totals']
        total_runs += 1
        if result:
            # Add a PASS to this script
            counts[0] = counts[0] + 1
            total_passes += 1
        else:
            # Add a FAILURE to this script
            counts[1] = counts[1] + 1
        # If passes and failures (= total runs) for this script
        # bigger than the current global total runs, update the
        # max_passes var, that is the max number of runs for all
        # scripts, needed to produce the results histogram.
        if (counts[0] + counts[1]) > max_passes:
            max_passes = counts[0] + counts[1]
        # Update the passes and failures for this scipt
        scripts_d[script]['totals'] = counts
        scripts_d[script]['iters'].append({'time': duration, 'result': result, 'log': log})
    return scripts_d, max_passes, total_runs, total_passes


def print_results(args, scripts_d, max_passes, total_runs, total_passes):
    # Reset the histogram list
    histo = [0 for i in range(max_passes + 1)]

    # Create a histogram that counts how many scripts have each number of
    # passes
    for s in scripts_d:
        histo[scripts_d[s]['totals'][0]] = histo[scripts_d[s]['totals'][0]] + 1

    scripts_ordered_l = sorted(scripts_d.items(), key=lambda x: x[1]['totals'][0], reverse=True)

    prev = -1
    first = True
    for s, d in scripts_ordered_l:
        if args.group:
            if d['totals'][0] != prev:
                # Start new group of passes
                prev = d['totals'][0]
                if not first:
                    print
                first = False
                print "Scripts that passed %d times:" % (prev)
                print "-----------------------------"

            print "%s" % (s)
        else:
            print "%s: %d Passed, %d Failed" % (s, d['totals'][0], d['totals'][1])
    print
    print "Total scripts: ", len(scripts_d), ", total iterations: ", max_passes
    print "Total runs: ", total_runs, ", total passes: ", total_passes, ", duplicate results: ", len(
        dups), ", missed results: ", len(missed)
    print
    print "Passes histogram: "
    for i in range(max_passes + 1):
        print "%4d " % i,

    print
    for i in range(max_passes + 1):
        print "%4d " % histo[i],

    print
    print
    print "Consistently failed: "
    for s in scripts_d:
        if scripts_d[s]['totals'][0] == 0:
            print s

    return histo



def create_xml_report(log_dict):

    if args.minpass is None or args.iterations is None:
        print "Error: MINPASS and ITERATIONS should be defined as parameters in order to produce xml report"
        print "Skipping XML report"
        return


    try:
        from junit_xml import TestSuite, TestCase
    except ImportError as e:
        print "Could not import junit_xml.Thus no xml can be produced"
        return


    def tst_suite_tst_case_dict():
        return {'testSuite': TestSuite(''),
                'testCases': []
                }

    test_suites_to_test_cases = defaultdict(tst_suite_tst_case_dict)

    pass_iterations = 0
    failed_iterations = []
    error_output = ''
    iterations = args.iterations  # should be parameterized
    print 'Going for {i} iterations'.format(i=iterations)
    aggregated_time = 0
    epoch = datetime.utcfromtimestamp(0)


    for script_name in log_dict:
        package_name = script_name.split('/')[1]
        group_name = script_name.split('/')[2]

        test_suite = test_suites_to_test_cases[package_name]['testSuite']
        test_suite.name = package_name
        test_suite.package = package_name
        test_suite.test_cases = test_suites_to_test_cases[package_name]['testCases']

        for i in range(iterations):
            aggregated_time += log_dict[script_name]['iters'][i]['time']
            if 'FAILED' in log_dict[script_name]['iters'][i]['log']:
                # do some truncation first in case the log is too big
                log_lines = log_dict[script_name]['iters'][i]['log'].split('\n')
                tail_lines = 10
                keep_log = '\n'.join(log_lines[:3]) + \
                           '\n' * 2 + '*** MESSAGE TRUNCATED ***' + '\n' * 2 + \
                           '\n'.join(log_lines[-tail_lines:])

                failed_iterations.append({'iteration': i, 'log': keep_log})
            else:
                pass_iterations += 1

        test = TestCase(script_name.split('/')[-1],
                        classname=test_suite.package + '.' + group_name,
                        elapsed_sec=aggregated_time
                        )

        if failed_iterations:
            for failed_case in failed_iterations:
                error_output += '\n' + 'Iteration: ' + str(failed_case['iteration']) + '\n' * 2 + \
                                'Reason: ' + '\n' + failed_case['log']

            test.stderr = error_output

        if pass_iterations < args.minpass:
            test.add_failure_info(message="More info below", output=error_output)
            test.stderr = ''

        test_suite.test_cases.append(test)
        failed_iterations = []
        pass_iterations = 0
        error_output = ''
        aggregated_time = 0

    for suite_name in test_suites_to_test_cases:
        sleep(1)
        with open('junit_' + str((datetime.now() - epoch).total_seconds() * 1000) + '_' + suite_name + '.xml',
                  'w') as f:
            TestSuite.to_file(f, [test_suites_to_test_cases[suite_name]['testSuite']])


def compute_exit_code(args, total_runs, total_passes, histo):
    # Compute exit code
    if args.strict:
        if total_runs != total_passes:
            print "\nFAILURE: Not all scripts PASS, and -s has been selected"
            return 1
        else:
            print "\nSUCCESS: All scripts PASS, and -s has been selected"
            return 0

    if args.minpass:
        minpass = True
        for i in range(args.minpass):
            if histo[i] != 0:
                minpass = False
                break

        if not minpass:
            print "\nFAILURE: Not all scripts PASSED at least %d time(s)" % (args.minpass)
            return 1
        elif not args.percent:
            print "\nSUCCESS: All scripts PASSED at least %d time(s)" % (args.minpass)
            return 0

    if args.percent:
        pct = 100 * total_passes / total_runs

        if pct < args.percent:
            print "\nFAILURE: PASSED percentage: %d, threshold was set to %d using -p" % (pct, args.percent)
            return 1
        elif not args.minpass:
            print "\nSUCCESS: PASSED percentage: %d, threshold was set to %d using -p" % (pct, args.percent)
            return 0

    if args.percent and args.minpass:
        print "\nSUCCESS: PASSED percentage: %d, threshold was set to %d using -p, and all scripts PASSED at least %d time(s)" % (
        pct, args.percent, args.minpass)
        return 0

    return 0


args = parse_args()
parse_log(args.log_file)
scripts_d, max_passes, total_runs, total_passes = process_results()
create_xml_report(scripts_d)
histo = print_results(args, scripts_d, max_passes, total_runs, total_passes)
r = compute_exit_code(args, total_runs, total_passes, histo)

exit(r)
