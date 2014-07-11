#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import distutils
import distutils.ccompiler
import sys


def parallelise_distutils(jobs):
    try:
        import multiprocessing  # noqa
        import multiprocessing.pool  # noqa
    except:
        print "Error: multiprocessing.pool not available"
        return False

    if sys.version_info[1] != 7:
        return False

    def _parallel_compile(*args, **kwargs):
        return parallel_compile(*args, jobs=jobs, **kwargs)

    distutils.ccompiler.CCompiler.compile = _parallel_compile
    return True


# Reference: http://goo.gl/f6wO0F
def parallel_compile(self, sources,
                     output_dir=None,
                     macros=None,
                     include_dirs=None,
                     debug=0,
                     extra_preargs=None,
                     extra_postargs=None,
                     depends=None,
                     jobs=1):
    # Copied from distutils.ccompiler.CCompiler
    macros, objects, extra_postargs, pp_opts, build = self._setup_compile(
        output_dir, macros, include_dirs, sources, depends, extra_postargs)

    cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)

    def _single_compile(obj):
        try:
            src, ext = build[obj]
        except KeyError:
            return

        self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)

    try:
        import multiprocessing.pool as pool
        list(pool.ThreadPool(jobs).imap(_single_compile, objects))
    except ImportError:
        pass

    return objects
