from proto.TextCore import TextCore as ProtoTextCore


class TextCore(ProtoTextCore):
    @staticmethod
    def _getHtmlCoreCls():
        from proto.hyperbrowser.HtmlCore import HtmlCore as HbHtmlCore
        return HbHtmlCore
