# coding:utf-8
from vn_data.replies import rules
from pprint import pprint


class RepliesMatch:
    def __init__(self, rule, string, lang='en'):
        self._rule = rule
        self._string = string.strip().lower()
        self._lang = lang
        self._mixed = None
        self._matched = False
        self.match()

    def match(self):
        for r in self._rule['matching']:
            # mix keys
            self._mixed = self.mix2(r['keys'])

            # check matched
            if 'strictly' == r['mode']:
                self._matched = self.match_strictly()
            elif 'orderly' == r['mode']:
                self._matched = self.match_orderly()
            elif 'disorderly' == r['mode']:
                self._matched = self.match_disorderly()

            if self._matched:
                return True

    @property
    def replies(self):
        if self._matched is True:
            return self._rule['replies'][self._lang]
        return {}

    def mix(self, arr, i=1, target=None):
        result = []

        if 1 > len(arr):
            return result

        if 1 == len(arr):
            return arr[0]

        if target is None:
            target = arr[0]

        for s in target:
            for e in arr[i]:
                if not e.strip():
                    r = e
                else:
                    r = '%s|%s' % (s, e)

                if r not in result:
                    result.append(r)

        if i < len(arr) - 1:
            return self.mix(arr, i+1, result)

        return result

    def mix2(self, arr, i=1, target=None):
        # results with '|'
        ss = []

        if 1 > len(arr):
            return ss

        if 1 == len(arr):
            return arr[0]

        if target is None:
            target = arr[0]

        for s in target:
            for e in arr[i]:
                if not e.strip():
                    r = e
                else:
                    r = '%s|%s' % (s, e)

                if r not in ss:
                    ss.append(r)

        if i < len(arr) - 1:
            return self.mix2(arr, i+1, ss)

        # results without '|'
        results = []
        for row in ss:
            results.append(row.split('|'))

        return results

    def match_strictly(self):
        for mixed in self._mixed:
            if ''.join(mixed) == self._string:
                return True
        return False

    def match_orderly(self):
        for mixed in self._mixed:
            p = []
            for e in mixed:
                p.append(self._string.find(e))
            if -1 not in p and p == sorted(p):
                return True
        return False

    def match_disorderly(self):
        for mixed in self._mixed:
            matched = True
            for row in mixed:
                if row not in self._string:
                    matched = False
            if matched is True:
                return True
        return False


def get_matched_replies(s, lang='en'):
    for rule in rules:
        rm = RepliesMatch(rule, s, lang)
        if rm.replies:
            return rm.replies
    return None
