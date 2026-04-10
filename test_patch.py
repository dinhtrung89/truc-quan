import pandas as pd

try:
    from pandas.util._decorators import deprecate_kwarg
except ImportError:
    def deprecate_kwarg(old_arg_name, new_arg_name, mapping=None, stacklevel=2):
        def _deprecate_kwarg(func):
            return func
        return _deprecate_kwarg
    import pandas.util._decorators
    pandas.util._decorators.deprecate_kwarg = deprecate_kwarg

from pandas_datareader import wb

if __name__ == "__main__":
    df = wb.download(indicator='NY.GDP.MKTP.KD.ZG', country='VNM', start=2010, end=2015)
    print(df.head())
