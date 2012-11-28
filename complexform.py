# -*- coding: UTF-8 -*-
# vim: set ts=4 sw=4 expandtab :

import string

from werkzeug.datastructures import TypeConversionDict, ImmutableDictMixin
from flask.wrappers import Request

class ComplexForm(TypeConversionDict):
   def __init__(self, mapping=None): 
        if isinstance(mapping, (dict, ComplexForm)):
            dict.__init__(self, unflat_dict(mapping.items()))

        else:
            dict.__init__(self, unflat_dict(mapping or ()))

class ImmutableComplexForm(ImmutableDictMixin, ComplexForm):
    def copy(self):
        return ComplexForm(self)

    def __copy__(self):
        return self

class ComplexFormRequest(Request):
    parameter_storage_class = ComplexForm

VALID_ID = string.ascii_letters + "_" + string.digits

def parse_field_name(s):
    def _next(i):
        try:
            return next(i)

        except StopIteration:
            return None

    ret = []
    i = iter(s)
    c = _next(i)
    name = ""

    while c and (c in VALID_ID):
        name += c
        c = _next(i)

    ret.append(name)

    if not name:
        ret.append(False)

        return ret

    while c:
        if c == "[":
            c = _next(i)
            name = ""

            while c and (c in VALID_ID):
                name += c
                c = _next(i)

            if c == "]":
                ret.append(name)
                name = ""
                c = _next(i)

            else:
                ret.append(False)

                break

        else:
            ret.append(False)

            break

    return ret

def check_array_ref(s):
    try:
        if s == "":
            return True

        int(s)

        return True

    except ValueError:
        return False

def unflat_dict(data):
    ret = {}

    for k, v in data:
        kp = parse_field_name(k)

        if kp[-1] is False:
            continue # erro de sintaxe

        ref = ret
        kp_counter = 0

        while kp_counter < len(kp) - 1:
            sk = kp[kp_counter]
            is_array_ref = check_array_ref(kp[kp_counter])
            is_array = (type(ref) != dict)

            if is_array_ref != is_array:
                continue # atribuição incompatível

            is_array_next = check_array_ref(kp[kp_counter + 1])

            if is_array:
                idx = None
                key_exists = False

                if sk == "": 
                    ref.append(None)
                    idx = len(ref) - 1

                else:
                    idx = int(sk)

                    if idx > len(ref) - 1:
                        delta = idx - len(ref) + 1
                        ref.extend([None] * delta)

                    else:
                        key_exists = (ref[idx] is not None)

                if not key_exists:
                    ref[idx] = [] if is_array_next else {}
                    ref = ref[idx]

                else:
                    ref = ref[idx]

            else:
                if not ref.has_key(sk):
                    ref[sk] = [] if is_array_next else {}
                    ref = ref[sk]

                else:
                    ref = ref[sk]

            kp_counter += 1

        lk = kp[kp_counter]
        is_array_ref = check_array_ref(lk)
        is_array = (type(ref) != dict)

        if is_array_ref != is_array:
            continue # atribuição incompatível

        if is_array_ref:
            if lk == "": 
                ref.append(v)

            else:
                idx = int(lk)

                if idx > len(ref) - 1:
                    delta = idx - len(ref) + 1
                    ref.extend([None] * delta)

                ref[idx] = v

        else:
            ref[lk] = v

    return ret
