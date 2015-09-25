from importlib import import_module

from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from mezzanine import template
from mezzanine.conf import settings


register = template.Library()


CUSTOM_FIELD_RENDERER = getattr(settings, 'ADVANCED_ADMIN_FIELD_RENDERER',
                                'mezzanine_advanced_admin.renderers.BootstrapFieldRenderer')


@register.simple_tag(takes_context=True)
def render_with_template_if_exist(context, template, fallback):
    text = fallback
    try:
        text = render_to_string(template, context)
    except:
        pass
    return text

@register.simple_tag(takes_context=True)
def language_selector(context):
    """ displays a language selector dropdown in the admin, based on Django "LANGUAGES" context.
        requires:
            * USE_I18N = True / settings.py
            * LANGUAGES specified / settings.py (otherwise all Django locales will be displayed)
            * "set_language" url configured (see https://docs.djangoproject.com/en/dev/topics/i18n/translation/#the-set-language-redirect-view)
    """
    output = ""
    i18 = getattr(settings, 'USE_I18N', False)
    if i18:
        template = "admin/language_selector.html"
        context['i18n_is_set'] = True
        try:
            output = render_to_string(template, context)
        except:
            pass
    return output


@register.filter(name='column_width')
def column_width(value):
    try:
        return 12 // len(list(value))
    except ZeroDivisionError:
        return 12


@register.filter(name='form_fieldset_column_width')
def form_fieldset_column_width(form):
    # def max_line(fieldset):
    #     return max([len(list(line)) for line in fieldset])
    #
    # try:
    #     width = max([max_line(fieldset) for fieldset in form])
    #     return 12 // width
    # except ValueError:
    #     return 12
    return 12


@register.filter(name='fieldset_column_width')
def fieldset_column_width(fieldset):
    try:
        width = max([len(list(line)) for line in fieldset])
        return 12 // width
    except ValueError:
        return 12


@register.simple_tag(takes_context=True)
def render_app_name(context, app, template="/admin_app_name.html"):
    """ Render the application name using the default template name. If it cannot find a
        template matching the given path, fallback to the application name.
    """
    try:
        template = app['app_label'] + template
        text = render_to_string(template, context)
    except:
        text = app['name']
    return text


@register.simple_tag(takes_context=True)
def render_app_label(context, app, fallback=""):
    """ Render the application label.
    """
    try:
        text = app['app_label']
    except KeyError:
        text = fallback
    except TypeError:
        text = app
    return text


@register.simple_tag(takes_context=True)
def render_app_description(context, app, fallback="", template="/admin_app_description.html"):
    """ Render the application description using the default template name. If it cannot find a
        template matching the given path, fallback to the fallback argument.
    """
    try:
        template = app['app_label'] + template
        text = render_to_string(template, context)
    except:
        text = fallback
    return text


@register.simple_tag(takes_context=True, name="dab_field_rendering")
def custom_field_rendering(context, field, *args, **kwargs):
    """ Wrapper for rendering the field via an external renderer """
    if CUSTOM_FIELD_RENDERER:
        mod, cls = CUSTOM_FIELD_RENDERER.rsplit(".", 1)
        field_renderer = getattr(import_module(mod), cls)
        if field_renderer:
            return field_renderer(field, **kwargs).render()
    return field


@register.as_tag
def get_menus_for_page(page=None):
    """
    Get menus labels for page.
    """
    if not page:
        return settings.PAGE_MENU_TEMPLATES
    menus = []
    for menu in settings.PAGE_MENU_TEMPLATES:
        if str(menu[0]) in page.in_menus:
            menus.append(menu[1])
    return menus


@register.simple_tag
def get_content_model_for_page(page):
    """
    Render the page content model label.
    """
    return unicode(page.get_content_model()._meta.verbose_name)


@register.inclusion_tag("admin/includes/admin_title.html", takes_context=True)
def admin_title(context):
    title = getattr(settings, "ADVANCED_ADMIN_TITLE", _("%s - Administration" % settings.SITE_TITLE))
    logo_path = getattr(settings, "ADVANCED_ADMIN_LOGO_PATH", None)
    context["title"] = title
    context["logo_path"] = logo_path
    return context

@register.inclusion_tag("admin/includes/menu.html", takes_context=True)
def render_menu(context):
    return  context


@register.filter(name='widget_type')
def widget_type(field):
    """
    Template filter that returns field widget class name (in lower case).
    E.g. if field's widget is TextInput then {{ field|widget_type }} will
    return 'textinput'.
    """
    if hasattr(field, 'field') and hasattr(field.field, 'widget') and field.field.widget:
        return field.field.widget.__class__.__name__.lower()
    return ''