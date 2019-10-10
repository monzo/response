import bleach
import bleach_whitelist


def sanitize(string):
    # bleach doesn't handle None so let's not pass it
    if string:
        return bleach.clean(
            string,
            tags=bleach_whitelist.markdown_tags,
            attributes=bleach_whitelist.markdown_attrs,
            styles=bleach_whitelist.all_styles,
        )

    return string
