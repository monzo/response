global STATUS_PAGE
STATUS_PAGE = None


def set_status_page_conn(conn):
    global STATUS_PAGE
    STATUS_PAGE = conn


def get_status_page_conn():
    global STATUS_PAGE
    return STATUS_PAGE
