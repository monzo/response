import bleach
import bleach_whitelist


def sanitize(string):
    return bleach.clean(
        string,
        tags=bleach_whitelist.markdown_tags,
        attributes=bleach_whitelist.markdown_attrs,
        styles=bleach_whitelist.all_styles,
    )
