import argparse
import sys

class ArgumentParserForBlender(argparse.ArgumentParser):
    def _get_argv_after_doubledash(self):
        try:
            idx = sys.argv.index("--")  
            return sys.argv[idx+1:]
        except ValueError as e:
            return []
        
    def parse_args(self):
        return super().parse_args(args=self._get_argv_after_doubledash())