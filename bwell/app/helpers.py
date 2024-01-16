from flask import Flask, url_for
from werkzeug.routing import Rule


def rule_has_no_empty_params(rule: Rule) -> bool:
    defaults = rule.defaults or ()
    arguments = rule.arguments or ()
    return len(defaults) >= len(arguments)


def app_get_endpoints(app: Flask) -> list[tuple[str, str]]:
    def make_endpoint(rule: Rule) -> tuple[str, str]:
        return (
            rule.endpoint,
            f'<a href="{(url:=url_for(rule.endpoint))}">{url}</a>'
            if rule_has_no_empty_params(rule)
            else "<unknown url>",
        )

    return [
        make_endpoint(rule)
        for rule in app.url_map.iter_rules()
    ]
