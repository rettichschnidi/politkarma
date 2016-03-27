from django import template

register = template.Library()


@register.inclusion_tag('tag_templates/karma_result_table.html')
def show_results(karma_results):
    print(karma_results)
    return {
        'results': karma_results.ranking,
        'start_date': karma_results.start_date,
        'end_date': karma_results.end_date,
        'cantons': ", ".join(karma_results.cantons),
        'organizations': ", ".join(karma_results.organizations),
        'import_date': karma_results.import_date,
    }
