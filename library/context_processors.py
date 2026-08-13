def library_context(request):
    """
    'Мугалим/админ' экенин бардык шаблондордо билүү үчүн.
    Уруксат эрежеси: суперпайдалануучу же 'Teachers' тобунун мүчөсү гана
    документ кошо алат. Студенттер (жөнөкөй катталган же анонимдүү
    колдонуучулар) — жок.
    """
    user = getattr(request, 'user', None)
    can_upload = bool(
        user and user.is_authenticated
        and (user.is_superuser or user.groups.filter(name='Teachers').exists())
    )
    return {'can_upload': can_upload}