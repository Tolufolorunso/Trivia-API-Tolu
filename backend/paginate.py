from flask import request


def paginate(selection, questions_per_page, page_number=1):
    start = (page_number - 1) * questions_per_page
    print(page_number)
    end = start + questions_per_page
    number_of_items = [x.format() for x in selection]

    return number_of_items[start:end]
