from Crumbs import Crumbs

#todo: add all the crumbs integrity checks here
class Inspector:
    @staticmethod
    def run_all_checks(crumbs):
        #todo don't throw exceptions, log everything instead
        Inspector.inspect_primers(crumbs)

    @staticmethod
    def inspect_primers(crumbs):
        primers = crumbs.primers.keys()
        for key, value in crumbs.story_cache["fundamentals"].items():
            if key == "context":
                continue
            if key in primers:
                #todo: also inspect whether all the sub-elements have an entry in the primer
                continue
            else:
                raise ValueError("Could not find primer for story element {0}".format(key))