from streamlink.plugins.f1tv import F1TV
from tests.plugins import PluginCanHandleUrl


class TestPluginCanHandleUrlF1TV(PluginCanHandleUrl):
    __plugin__ = F1TV

    should_match = [
        "https://f1tv.formula1.com/",
        "https://www.f1tv.formula1.com/",
        "https://f1tv.formula1.com/detail/1000000012",
        "https://f1tv.formula1.com/en/latest",
        "https://f1tv.formula1.com/en/page/12345",
        "https://f1tv.formula1.com/live",
    ]

    should_not_match = [
        "https://www.formula1.com/",
        "https://example.com/",
        "https://f1.com/",
    ]
