# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

"""
Wrapper for Vowpal Wabbit executable

TODO: 
-Detect VW version in unit tests; for command line generation scenarios,
    unit tests should detect whether it works as expected.
-Scenario assistance; e.g. caching examples for reuse in multi-pass
    (This would make good example code also.)
    -Abstraction for passes (with automatic usage of example cache)
-Example for README: Active learning interface
-Sklearn compatibility (like vowpal_porpoise)


by Michael J.T. O'Kelly, 2014-2-24
"""

__author__ = "Michael J.T. O'Kelly"
__email__ = 'mokelly@gmail.com'
__version__ = '0.3.0'

try:
    basestring
except:
    basestring = str

import logging
import re

import pexpect

from . import active_learner

class WabbitInvalidCharacter(ValueError):
    pass


validation_regex = re.compile(r' |:|\|')

def validate_vw_string(s):
    """Throw a WabbitInvalidCharacter exception if the string is
    not a 
    (http://stats.stackexchange.com/questions/28877/finding-the-best-features-in-interaction-models)
    """
    if validation_regex.search(s):
        raise WabbitInvalidCharacter(s)


escape_dict = {' ': r'\_',
               ':': r'\;',
               '|': r'\\'
               }

def escape_vw_character(special_character_re_match):
    special_character = special_character_re_match.group()
    return escape_dict[special_character]


def escape_vw_string(s):
    escaped_s = validation_regex.sub(escape_vw_character, s)
    return escaped_s


class Namespace():
    """Abstraction of Namespace part of VW example lines"""
    def __init__(self,
                 name=None,
                 scale=None,
                 features=None,
                 escape=True,
                 validate=True,
                 cache_string=False):
        """Create a namespace with given (optional) name and importance,
        initialized with any given features (described in add_features()).
        If 'validate', name and features are validated for compatibility
            with VW's reserved characters, throwing a WabbitInvalidCharacter
            exception.
        If 'escape', any invalid characters are replaced with escape characters.
            ('escape' mode supersedes 'vaildate' mode.)
        If 'cache_string', the results of any to_string() call are cached
            permanently, ignoring any further changes to self.  (This can
            speed things up if this Namespace is re-used.)
        """
        self.name = name
        self.scale = scale
        self.validate = validate
        self.escape = escape
        self._string = None
        self.features = []
        self.cache_string = cache_string
        if name:
            if escape:
                self.name = escape_vw_string(self.name)
            elif validate:
                validate_vw_string(self.name)
        if features:
            self.add_features(features)

    def add_features(self, features):
        """Add features to this namespace.
        features: An iterable of features.  A feature may be either
            1) A VW label (not containing characters from escape_dict.keys(),
                unless 'escape' mode is on)
            2) A tuple (label, value) where value is any float
        """
        for feature in features:
            if isinstance(feature, basestring):
                label = feature
                value = None
            else:
                label, value = feature
            self.add_feature(label, value)

    def add_feature(self, label, value=None):
        """
        label: A VW label (not containing characters from escape_dict.keys(),
            unless 'escape' mode is on)
        value: float giving the weight or magnitude of this feature
        """
        if self.escape:
            label = escape_vw_string(label)
        elif self.validate:
            validate_vw_string(label)
        feature = (label, value)
        self.features.append(feature)

    def to_string(self):
        """Export this namespace to a string suitable for incorporation
        in a VW example line, e.g.
        'MetricFeatures:3.28 height:1.5 length:2.0 '
        """
        if self._string is None:
            tokens = []
            if self.name:
                if self.scale:
                    token = self.name + ':' + str(self.scale)
                else:
                    token = self.name
            else:
                token = ''  # Spacing element to indicate next string is a feature
            tokens.append(token)
            for label, value in self.features:
                if value is None:
                    token = label
                else:
                    token = label + ':' + str(value)
                tokens.append(token)
            tokens.append('')  # Spacing element to separate from next pipe character
            output = ' '.join(tokens)
            if self.cache_string:
                self._string = output
        else:
            output = self._string
        return output

    def export_features(self, delimiter='\\'):
        """Export the features from this namespace as a list of feature tokens
        with the namespace name prepended (delimited by 'delimiter').

        Example:
        >>> namespace = Namespace('name1', features=['feature1', 'feature2'])
        >>> print namespace.export_features()
        ['name1\\feature1', 'name1\\feature2']
        """
        result_list = []
        for feature in self.features:
            result = '{}{}{}'.format(self.name, delimiter, feature)
            result_list.append(result)
        return result_list


class VWResult():
    """Parses VW string output into consistent structure"""
    def __init__(self, result_string, active_mode=False):
        """Set 'active_mode' to True to parse results in
        an Active Learning context."""
        self.raw_output = result_string
        result_list = []
        # TODO: Something more robust than whitespace splitting
        #   to handle modes like --audit ?
        for token in result_string.split():
            try:
                result = float(token)
                result_list.append(result)
            except ValueError:
                # Ignore tokens that can't be made into floats (like tags)
                logging.debug("Ignoring non-float token {}".format(token))
        self.value_list = result_list
        if result_list:
            self.prediction = result_list[0]
        else:
            self.prediction = None
        if active_mode:
            if len(result_list) > 1:
                self.importance = result_list[1]
            else:
                self.importance = 0.

    def __str__(self):
        return str(self.__dict__)


class VW():
    """Wrapper for VW executable, handling online input and outputs."""
    def __init__(self, command=None, active_mode=False, dummy_mode=False, daemon_mode=False,
                 daemon_ip=None, **kwargs):
        """'command' is the full command-line necessary to run VW.  E.g.
        vw --loss_function logistic -p /dev/stdout --quiet
        -p /dev/stdout --quiet is mandatory for compatibility,
        and certain options like 
            --save_resume
        are suggested, while some options make no sense in this context:
            -d
            --passes
        wabbit_wappa.py does not support any mode that turns off piping to
        stdin or stdout

        active_mode: Launch VW in port-listening active learning mode, controlled via
            a simulated subprocess.
        dummy_mode: Don't actually start any VW process.  (Used for assembling
            VW command lines separately.)
        daemon_mode: (Forced to True if active_mode is set).  Communicate with
            VW as a server instead of as a subprocess.
            NOTE: This is much faster in tests, and will become default in
            a future version of WW.
        daemon_ip: If given, attach to an already-running VW daemon, ignoring
            all other command-related arguments (other than `port`).

        If no command is given, any additional keyword arguments are passed to
            make_command_line() and the resulting command is used.  (This provides
            sensible defaults.)
        """
        daemon_mode = daemon_mode or active_mode
        if command is None:
            if active_mode:
                active_settings = active_learner.get_active_default_settings()
                # Overwrite active settings with kwargs
                active_settings.update(kwargs)
                kwargs = active_settings
            command = make_command_line(**kwargs)
        port = kwargs.get('port')
        self.active_mode = active_mode
        self.dummy_mode = dummy_mode
        self.daemon_mode = daemon_mode
        if dummy_mode:
            self.vw_process = None
        else:
            if active_mode or daemon_ip or daemon_mode:
                self.vw_process = active_learner.DaemonVWProcess(command,
                                                                 port=port,
                                                                 ip=daemon_ip)
            else:
                self.vw_process = pexpect.spawn(command)
                # Turn off delaybeforesend; this is necessary only in non-applicable cases
                self.vw_process.delaybeforesend = 0
                self.vw_process.setecho(False)
                logging.info("Started VW({})".format(command))
        self.command = command
        self.namespaces = []
        self._line = None

    def send_line(self, line, parse_result=True):
        """Submit a raw line of text to the VW instance, returning a 
        VWResult() object.

        If 'parse_result' is False, ignore the result and return None.
        """
        self.vw_process.sendline(line)  # Send line, along with newline
        result = self._get_response(parse_result=parse_result)
        return result

    def _get_response(self, parse_result=True):
        """If 'parse_result' is False, ignore the received output and return None."""
        # expect_exact is faster than just exact, and fine for our purpose
        # (http://pexpect.readthedocs.org/en/latest/api/pexpect.html#pexpect.spawn.expect_exact)
        # searchwindowsize and other attributes may also affect efficiency
        self.vw_process.expect_exact('\r\n', searchwindowsize=-1)  # Wait until process outputs a complete line
        if parse_result:
            output = self.vw_process.before
            result_struct = VWResult(output, active_mode=self.active_mode)
        else:
            result_struct = None
        return result_struct

    def send_example(self,
                     *args,
                     **kwargs
                     ):
        """Send a labeled or unlabeled example to the VW instance.
        If 'parse_result' kwarg is False, ignore the result and return None.

        All other parameters are passed to self.send_line().

        Returns a VWResult object.
        """
        # Pop out the keyword argument 'parse_result' if given
        parse_result = kwargs.pop('parse_result', True)
        line = self.make_line(*args, **kwargs)
        result = self.send_line(line, parse_result=parse_result)
        return result

    def make_line(self,
                  response=None,
                  importance=None,
                  base=None,
                  tag=None,
                  features=None,
                  namespaces=None,
                  ):
        """Makes and returns an example string in VW syntax.
        If given, 'response', 'importance', 'base', and 'tag' are used
        to label the example.  Features for the example come from
        any given features or namespaces, as well as any previously
        added namespaces (using them up in the process).
        """
        if namespaces is not None:
            self.add_namespaces(namespaces)
        if features is not None:
            namespace = Namespace(features=features)
            self.add_namespace(namespace)
        substrings = []
        tokens = []
        if response is not None:
            token = str(response)
            tokens.append(token)
            if importance is not None:  # Check only if response is given
                token = str(importance)
                tokens.append(token)
                if base is not None:  # Check only if importance is given
                    token = str(base)
                    tokens.append(token)
        if tag is not None: 
            token = "'" + str(tag)  # Tags are unambiguous if given a ' prefix
            tokens.append(token)
        else:
            token = ""  # Spacing element to avoid ambiguity in parsing
            tokens.append(token)
        substring = ' '.join(tokens)
        substrings.append(substring)
        if self.namespaces:
            for namespace in self.namespaces:
                substring = namespace.to_string()
                substrings.append(substring)
        else:
            substrings.append('')  # For correct syntax
        line = '|'.join(substrings)
        self._line = line
        self.namespaces = []  # Reset namespaces after their use
        return line

    def add_namespace(self, *args, **kwargs):
        """Accepts two calling patterns:
        add_namespace(namespace): queue a preexisting namespace onto
            this VW instance.
        add_namespace(name, scale, features, ...): Pass all args and kwargs
            to the Namespace constructor to make a new Namespace instance,
            and queue it to this VW instance.

        Returns self (so that this command can be chained).
        """
        if args and isinstance(args[0], Namespace):
            namespace = args[0]
        elif isinstance(kwargs.get('namespace'), Namespace):
            namespace = kwargs.get('namespace')
        else:
            namespace = Namespace(*args, **kwargs)
        self.namespaces.append(namespace)
        return self

    def add_namespaces(self, namespaces):
        """Add these namespaces sequentially.
        Returns self (so that this command can be chained)."""
        for namespace in namespaces:
            self.add_namespace(namespace)
        return self

    def get_prediction(self, features=None, tag=None, namespaces=None):
        """Send an unlabeled example to the trained VW instance.
        Uses any given features or namespaces, as well as any previously
        added namespaces (using them up in the process).

        Returns a VWResult object."""
        if features is not None:
            namespace = Namespace(features=features)
            self.add_namespace(namespace)
        result = self.send_example(tag=tag, namespaces=namespaces)
        return result

    def save_model(self, model_filename):
        """Pass a "command example" to the VW subprocess requesting
        that the current model be serialized to model_filename immediately.
        """
        line = "save_{}|".format(model_filename)
        self.vw_process.sendline(line)
        # No response is expected in this case

    def close(self):
        """Shut down the VW process."""
        self.vw_process.close()
        # TODO: Give this a context manager interface

    # TODO: Fancy interface for auditing data?


def make_command_line(predictions='/dev/stdout',
                      quiet=True,
                      save_resume=True,
                      q_colon=None,
                      **kwargs
                      ):
    """Construct a command line for VW, with each named argument corresponding
    to a VW option.
    Single character keys are mapped to single-dash options,
    e.g. 'b=20' yields '-b 20',
    while multiple character keys map to double-dash options:
        'quiet=True' yields '--quiet'
    Boolean values are interpreted as flags: present if True, absent if False.
    All other values are treated as option arguments, as in the -b example above.
    If an option argument is a list, that option is repeated multiple times,
    e.g. 'q=['ab', 'bc']' yields '-q ab -q bc'

    q_colon is handled specially, mapping to '--q:'.

    Run 'vw -h' for a listing of most options.

    Defaults are well-suited for use with Wabbit Wappa:
    vw --predictions /dev/stdout --quiet --save_resume

    NOTE: This function makes no attempt to validate the inputs or
    ensure they are compatible with Wabbit Wappa.

    Outputs a command line string.
    """
    args = ['vw']
    if q_colon:
        kwargs['q:'] = q_colon
    kwargs['predictions'] = predictions
    kwargs['quiet'] = quiet
    kwargs['save_resume'] = save_resume
    for key, value in kwargs.items():
        if len(key)==1:
            option = '-{}'.format(key)
        else:
            option = '--{}'.format(key)
        if value is True:
            arg_list = [option]
        elif isinstance(value, basestring):
            arg_list = ['{} {}'.format(option, value)]
        elif hasattr(value, '__getitem__'):  # Listlike value
            arg_list = [ '{} {}'.format(option, subvalue) for subvalue in value ]
        else:
            arg_list = ['{} {}'.format(option, value)]
        args.extend(arg_list)
    command = ' '.join(args)
    return command





